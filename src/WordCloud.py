import psycopg2
import os
import nltk
import re
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import CountVectorizer
from wordcloud import WordCloud
from nltk.corpus import stopwords
from dotenv import load_dotenv


class MountainProjectWordCloud(object):
    def __init__(self, username: str, password: str, host: str, port: str, database: str):
        """
        Initialize the connection and a cursor to execute queries with

        :param username: Username to connect to the database with
        :param password: Password to connect to the database with
        :param host: Host to connect to the database with
        :param port: Port to connect to the database with
        :param database: Database to connect to
        """
        self.connection = psycopg2.connect(user=username,
                                           password=password,
                                           host=host,
                                           port=port,
                                           database=database)

        self.cursor = self.connection.cursor()

    def fetchRouteCommentsByUserId(self, userId: int):
        """
        Fetch comments made by a specific user on routes

        :param userId: UserId of commenter
        :return: List of comments
        """
        query = """
            SELECT CommentBody
                FROM RouteComments
                WHERE UserId = %(userId)s
        """
        self.cursor.execute(query, {"userId": userId})

        return [x[0] for x in self.cursor.fetchall()]

    def fetchAreaCommentsByUserId(self, userId: int):
        """
        Fetch comments made by a specific user on areas

        :param userId: UserId of commenter
        :return: List of comments
        """
        query = """
            SELECT CommentBody
                FROM AreaComments
                WHERE UserId = %(userId)s
                """
        self.cursor.execute(query, {"userId": userId})

        return [x[0] for x in self.cursor.fetchall()]

    def createWordCloud(self,
                        userId: int,
                        savePath: str = None,
                        ngram_range: int = 1,
                        routeComments: bool = True,
                        areaComments: bool = False) -> None:
        if not routeComments and not areaComments:
            raise ValueError("At least one of routeComments and areaComments must be true.")

        comments = []

        if routeComments:
            comments.extend(self.fetchRouteCommentsByUserId(userId=userId))

        if areaComments:
            comments.extend(self.fetchAreaCommentsByUserId(userId=userId))

        wordFrequencies, stopWords = self.processComments(comments=comments, ngram_range=ngram_range)

        words = dict(wordFrequencies)
        wordCloudHeight = 1920
        wordCloudWidth = 1080
        wordCloudMaxWords = 200

        wordCloud = WordCloud(
            max_words=wordCloudMaxWords,
            height=wordCloudHeight,
            width=wordCloudWidth,
            stopwords=stopWords
        )

        wordCloud.generate_from_frequencies(words)
        plt.imshow(wordCloud, interpolation="bilinear")
        plt.axis("off")
        plt.show()

        if savePath:
            wordCloud.to_file(savePath)

    @staticmethod
    def processComments(comments: list, ngram_range: int = 1) -> tuple:
        # Init lemmatizer and vectorizer
        lemmatizer = nltk.WordNetLemmatizer()
        vectorizer = CountVectorizer(ngram_range=(ngram_range, ngram_range))

        # Clean the text some
        text = " ".join(comments)
        text = text.lower()
        text = text.replace(r"'", "")  # Remove single quotes
        text = text.replace(r". ", "")  # Remove periods followed by spaces. We can't lose 5.11 etc
        text = text.replace(r".\r", "")  # Remove periods followed by carriage returns
        text = text.replace(r".\n", "")  # Remove periods followed by newlines

        # Tokenize
        tokens = nltk.word_tokenize(text)
        text = nltk.Text(tokens)

        textContent = [
            "".join(re.split(pattern=r"[ ,;:!?‘’``''@#$%^_&*()<>{}~\n\t\\\-]", string=word)) for word in text
        ]

        # Fix stop words
        stopWords = set(stopwords.words("english"))
        stopWords.remove("not")  # Not is likely an important word in this case, especially as we will consider bigrams

        # Clean the tokens a bit
        textContent = [word for word in textContent if word not in stopWords and len(word) > 0]
        textContent = [lemmatizer.lemmatize(word) for word in textContent]

        # Interested in bigrams
        ngrams = list(nltk.ngrams(textContent, ngram_range))
        nramsText = [" ".join(ngram) for ngram in ngrams]

        # Vectorize
        bagOfWords = vectorizer.fit_transform(nramsText)
        sumWords = bagOfWords.sum(axis=0)
        wordFrequencies = [(word, sumWords[0, idx]) for word, idx in vectorizer.vocabulary_.items()]
        wordFrequencies.sort(key=lambda x: x[1], reverse=True)

        return wordFrequencies, stopWords


def main() -> None:
    load_dotenv()
    password = os.getenv("POSTGRESQL_PASSWORD")
    cloud = MountainProjectWordCloud(username="postgres",
                                     password=password,
                                     host="127.0.0.1",
                                     port="5432",
                                     database="MountainProject")

    cloud.createWordCloud(
        userId=10232,
        ngram_range=2,
        routeComments=True,
        areaComments=False,
        savePath="../img/Tony_B_Word_Cloud_Routes_Routes_2.png"
    )
    # print(comments)
    # print(type(comments))


if __name__ == "__main__":
    main()
