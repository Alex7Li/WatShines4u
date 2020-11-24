import csv

from watShines4u import watson


def upload() -> None:
    with open("data/date-reviews.csv") as file:
        reader = csv.reader(file)

        next(reader)  # skips headers

        for name, review in reader:
            data = {"name": name, "text": review}
            watson.add_document(data)


if __name__ == "__main__":
    print("Already uploaded.")
