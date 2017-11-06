from crawler import crawler
import pprint
import sqlite3 as sql

if __name__ == "__main__":
    dbFile = 'dbFile1.db'
    crawler(dbFile, "urls.txt")
    con = sql.connect(dbFile)
    cur = con.cursor()
    query = """
        SELECT docIndex.url, pageRank.score
        FROM pageRank, docIndex
        WHERE pageRank.docid = docIndex.docid
        ORDER BY pageRank.score DESC"""
    cur.execute(query)
    ranks = cur.fetchall()
    con.close()
    print "Page Rank Scores per URL:"
    pprint.pprint(ranks)
