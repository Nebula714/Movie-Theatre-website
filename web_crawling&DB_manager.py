# coding=utf-8

# if PyMySQL not install before, install for manipulating mysql database
# %pip install pymysql

import time
import requests
import pandas as pd
from bs4 import BeautifulSoup, Comment, SoupStrainer

import pymysql


db_config = {'host': 'localhost',
             'user': 'root',
             'password': '123456',
             'database': 'mysql',
             'charset': 'utf8',
             'cursorclass': pymysql.cursors.DictCursor}


def connect_db():
    try:
        # connect to mysql database
        conn = pymysql.connect(**db_config)

    except mysql.connector.Error as e:
        print('DATABASE Connection Error Occur: ', e)

    return conn



def extract_movie_info(movie_info, end_url_list, html):
    html = requests.get(html)

    # get source page with content property
    # resolve with BeautifulSoap and transfer into BS class
    soup = BeautifulSoup(html.content, 'lxml')

    table_list = soup.find("table", id='DataNowshowingListing')
    table_movies = table_list.find("table", width='650')

    # find movie image info from DataNowshowingListing
    for tbl in table_movies.find_all('table', width="650"):
        tds = tbl.find_all('td', class_='mtitle-listing-txt')

        movie_info[tbl.select('img')[0]['title']] = {'title': tbl.select('img')[0]['alt'],
                                                     'poster_src': tbl.select('img')[0]['src'],
                                                     'title_EN': tds[0].text,
                                                     'title_CN': tds[1].text
                                                     }

        titles = tbl.find_all('td', class_='mdetail-listing-txt')
        infos = tbl.find_all('td', class_='mdetail-b-listing-txt')

        movie_info[tbl.select('img')[0]['title']][titles[0].text] = infos[0].text
        movie_info[tbl.select('img')[0]['title']][titles[2].text] = infos[1].text
        movie_info[tbl.select('img')[0]['title']][titles[4].text] = infos[2].text
        movie_info[tbl.select('img')[0]['title']]['introduction'] = titles[6].text

    # get all sub_url for detailed info
    for i in soup.find_all('span', class_='listing-but'):
        if i.text == 'INFO':
            item = i.find_all('a')
            for j in item:
                end_url = j.get('href')
                if end_url not in end_url_list:
                    end_url_list.append(j.get('href'))

    time.sleep(10)



# extract data from webpage
movie_info = {}
end_url_list = []

for i in range(1, 4):
    extract_movie_info(movie_info, end_url_list,
                       'https://www.wecinemas.com.sg/listing.aspx?tab=nowshowing&Page={}'.format(i))




def extract_detailed_movie_info(movie_info, html):
    # extract data from webpage
    html = requests.get(html)

    # get source page with content property
    # resolve with BeautifulSoap and transfer into BS class
    info = BeautifulSoup(html.content, 'lxml')

    dmovie_info = info.find("table", width='436')

    movie_title = dmovie_info.find_all('span', id='lblMovieTitle')[0].text

    if movie_title in movie_info.keys():

        movie_AKA = dmovie_info.find_all('span', id='lblMovieAKA')[0].text
        titles = dmovie_info.find_all('td', class_='mdetail-listing-txt')
        infos = dmovie_info.find_all('td', class_='mdetail-b-listing-txt')
        intro = dmovie_info.find_all('td', class_='content-details-txt')

        movie_info[movie_title]['AKA'] = movie_AKA
        movie_info[movie_title]['Opening Date'] = dmovie_info.find_all('span', id='lblMovieReleaseDate')[0].text
        movie_info[movie_title]['Director'] = dmovie_info.find_all('span', id='lblMovieDirector')[0].text
        movie_info[movie_title]['Cast'] = dmovie_info.find_all('span', id='lblMovieCast')[0].text
        movie_info[movie_title]['Ratings'] = dmovie_info.find_all('span', id='lblMovieRating')[0].text
        movie_info[movie_title]['Duration'] = dmovie_info.find_all('span', id='lblMovieRuntime')[0].text
        movie_info[movie_title]['Language'] = dmovie_info.find_all('span', id='lblMovieLanguage')[0].text
        movie_info[movie_title]['Genre'] = dmovie_info.find_all('span', id='lblMovieGenre')[0].text
        movie_info[movie_title]['introduction'] = dmovie_info.find_all('span', id='lblMovieSynopsis')[0].text

        showtime = dmovie_info.find_all('option')

        movie_info[movie_title]['showdate'] = []

        for st in showtime:
            movie_info[movie_title]['showdate'].append(st.text)

        movie_info[movie_title]['showtime'] = dmovie_info.find_all('div', class_="showtimes-but")[0].text

        rmovie_info = info.find("table", width='436')
        recommend_movie = []

        rec_imgs = rmovie_info.find_all('img')
        rec_titles = rmovie_info.find_all('td', class_='mtitle-details-txt')
        rec_dates = rmovie_info.find_all('td', class_='mdate-home-txt')

        for i in range(len(rec_imgs)):
            recommend_movie.append([rec_imgs[i]['src'], rec_titles[i].text, rec_dates[i].text])

        movie_info[movie_title]['recommended_movie'] = recommend_movie



detail_movie_html = []
base_url = 'https://www.wecinemas.com.sg{}'

for end_url in end_url_list:
    url = base_url.format(end_url)

    extract_detailed_movie_info(movie_info, url)




# connect to database
db = connect_db()

# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db.cursor()




# create tables to store theatre data----- movie_info

sql = """
    CREATE TABLE movie_showing (
          title  VARCHAR(1000) NOT NULL,
          AKA VARCHAR(1000),
          title_EN  VARCHAR(1000),
          title_CN  VARCHAR(1000),
          poster_src VARCHAR(1000),
          opening_date VARCHAR(100),
          ratings VARCHAR(200),
          duration VARCHAR(100),
          director VARCHAR(500),
          cast VARCHAR(1000),
          language VARCHAR(200),
          genre VARCHAR(200),
          introduction VARCHAR(1000),
          showdate VARCHAR(2000),
          showtime VARCHAR(200),
          recommended_movie VARCHAR(1000)
          )
    """

cursor.execute(sql)
db.commit()


sql = 'insert into movie_showing values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

for mv_info in movie_info.values():
    data = (mv_info['title'], mv_info['AKA'], mv_info['title_EN'], mv_info['title_CN'],
            mv_info['poster_src'], mv_info['Opening Date'], mv_info['Ratings'], mv_info['Duration'],
            mv_info['Director'], mv_info['Cast'], mv_info['Language'], mv_info['Genre'],
            mv_info['introduction'], str(mv_info['showdate']), str(mv_info['showtime']),
            str(mv_info['recommended_movie']))

    cursor.execute(sql, data)

db.commit()





# create tables to store theatre data----- movie_info

sql = """
    CREATE TABLE manager_info (
          phone  VARCHAR(100) NOT NULL,
          password VARCHAR(100) NOT NULL
          )
    """

cursor.execute(sql)
db.commit()



manager_info = [['12345678', 'manager01'], ['12345679', 'manager02'], ['12345670', 'manager03']]

sql = 'insert into manager_info values (%s, %s)'

for manager in manager_info:
    info = (manager[0], manager[1])
    cursor.execute(sql, info)

db.commit()




# fetch data request API
# example: table: 'movie_showing', length: 2
def on_data_fetch_request(table, length, *columns):
    if not columns:
        columns = '*'
        sql = 'SELECT {} FROM {}'.format(columns, table)
    else:
        columns = ','.join(list(columns[0]))
        sql = 'SELECT {} FROM {}'.format(columns, table)
    if length:
        sql += ' LIMIT {}'.format(length)

    db = connect_db()
    cur = db.cursor()
    cur.execute(sql)
    return cur.fetchall()




# order_type: insert, delete, update
# insert order example: insert(order_type) into {table} {condition[0](as columns)} values {condition[1](as values)}
# condition like: [(col1, col2, col3,...), (val1, val2, val3,...)]
# delete order example: delete(order_type) * from {table} where {condition}
# condition like: {col1:val1, col2:val2,...}
# update order example: update(order_type) {table} set {col='' where col1='' and col2=''}
# condition like: {'set': {}, 'where': {}}

def on_manage_db_request(order_type, table, condition):
    sql = ''
    if order_type.lower() == 'insert':
        sql = 'INSERT INTO {} {} VAlUES {}'.format(table, condition[0], condition[1])
    elif order_type.lower() == 'delete':
        con = ''
        for key, val in condition.items():
            con += f" {key}={val} and "
        sql = 'DELETE * from {} where {}'.format(table, con[:-5])
    elif order_type.lower() == 'update':
        set_con = ''
        for key, val in condition['set'].items():
            set_con += f" {key}={val} and "

        where_con = ''
        for key, val in condition['where'].items():
            where_con += f" {key}={val} and "

        sql = 'UPDATE {} SET {} where {}'.format(table, set_con[:-5], where_con[:-5])
    else:
        raise ValueError('Invalid order_type!!!')

    db = connect_db()
    cur = db.cursor()
    cur.execute(sql)
    return cur.fetchall()



# API test:
# on_manage_db_request('insert', 'movie', [('col1','col2','col3'), ('val1', 'val2', 'val3')])

# on_manage_db_request('delete', 'movie', {'col1':'val1', 'col2':'val2', 'col3':'val3'})

# on_manage_db_request('update', 'movie', {'set':{'col1':'val1', 'col2':'val2', 'col3':'val3'}, 'where':{'col4':'val4','col5':'val5', 'col6':'val6'}})



def on_query_manager_info(phone):
    sql = "SELECT password FROM manager_info where phone = '{}'".format(phone)

    db = connect_db()
    cur = db.cursor()
    cur.execute(sql)
    return cur.fetchall()



# API test
# on_query_manager_info('12345678')



# # create tables to store theatre data----- coming movie info

# sql="""
#     CREATE TABLE coming_movie (
#           title  VARCHAR(200) NOT NULL,
#           title_EN  VARCHAR(200),
#           title_CN  VARCHAR(200),
#           poster_src VARCHAR(200),
#           opening_date VARCHAR(20),
#           rating VARCHAR(200),
#           duration VARCHAR(20),
#           introduction VARCHAR(2000))
#     """

# cursor.execute(sql)
# db.commit()


# insert data into coming_movie table
# sql = 'insert into coming_movie values(%s, %s, %s, %s, %s, %s, %s, %s)'

# for mv_info in coming_movie_info.values():
#     data = (mv_info['title'], mv_info['title_EN'], mv_info['title_CN'], mv_info['poster_src'],
#          mv_info['Opening Date'], mv_info['Ratings'], mv_info['Duration'], mv_info['introduction'])

#     cursor.execute(sql, data)

# db.commit()




# # create tables to store theatre data----- detailed movie info

# sql="""
#     CREATE TABLE detailed_movie_info (
#           title  VARCHAR(200) NOT NULL,
#           AKA  VARCHAR(200),
#           opening_date VARCHAR(20),
#           director VARCHAR(200),
#           cast VARCHAR(200),
#           rating VARCHAR(200),
#           duration VARCHAR(20),
#           language VARCHAR(200),
#           genre VARCHAR(50),
#           introduction VARCHAR(2000),
#           showdate VARCHAR(100),
#           showtime VARCHAR(50),
#           recommended_movie VARCHAR(2000)
#           )
#     """

# cursor.execute(sql)
# db.commit()


# insert data into detailed_movie_info table
# sql = 'insert into detailed_movie_info values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

# for key, value in detailed_movie_info.items():
#     data = (key, value['AKA'], value['Opening Date'], value['Director'], value['Cast'],
#          value['Ratings'], value['Duration'], value['Language'], value['Genre'],
#          value['introduction'], str(value['showdate']), value['showtime'], str(value['recommended_movie']))

#     cursor.execute(sql, data)

# db.commit()






# coming_table_list = soup.find("table",id='DataComingSoonListing')

# # find movie image info from DataNowshowingListing
# coming_movie_info = {}
# for tbl in coming_table_list.find_all('table', width="650"):
#     tds = tbl.find_all('td', class_='mtitle-listing-txt')

#     coming_movie_info[tbl.select('img')[0]['title']] = {'title': tbl.select('img')[0]['alt'],
#                                                 'poster_src': tbl.select('img')[0]['src'],
#                                                 'title_EN': tds[0].text,
#                                                 'title_CN': tds[1].text
#                                                }

#     titles = tbl.find_all('td', class_='mdetail-listing-txt')
#     infos = tbl.find_all('td', class_='mdetail-b-listing-txt')

#     coming_movie_info[tbl.select('img')[0]['title']][titles[0].text] = infos[0].text
#     coming_movie_info[tbl.select('img')[0]['title']][titles[2].text] = infos[1].text
#     coming_movie_info[tbl.select('img')[0]['title']][titles[4].text] = infos[2].text
#     coming_movie_info[tbl.select('img')[0]['title']]['introduction'] = titles[6].text

