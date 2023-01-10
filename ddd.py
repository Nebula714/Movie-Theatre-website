import csv
import sqlite3

if __name__ == '__main__':
    with open("movie_data.csv", 'r', encoding='utf-8') as f:
        f_csv = csv.reader(f)
        head = next(f_csv)

        conn = sqlite3.connect('db.sqlite3')  # 连接数据库文件
        cur = conn.cursor()  # 获取游标
        cur.execute("delete from movie_movie")
        conn.commit()
        for row in f_csv:
            title = row[2]
            l = title.split(" (Digital)")
            print(l)
            cur.execute("insert into movie_movie(title, url, grade, duration,stock)values(?, ?,?, ?, ?)",
                        (l[0], row[3], row[7], row[8], 100))
            conn.commit()  # 提交数据库操作
        cur.close()
        conn.close()  # 关闭数据库连接
        # for row in f_csv:
        #
        #     print(row)
