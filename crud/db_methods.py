#By Ruth and Aayah
import cs304dbi as dbi
from flask import flash

def insert_movie(conn,tt,title,release,addedby):
    """
    This will insert movies into the into the database
    """
    curs=dbi.dict_cursor(conn)

    curs.execute("""
                select count(*) from movie where tt=%s
                """,[tt])

    found_items=curs.fetchone()
    print(found_items)

    if found_items['count(*)']==0:
        curs.execute("""
                    insert into movie(tt,title,`release`,addedby) values(%s,%s,%s,%s)
                    """,[tt,title,release,addedby])
        conn.commit()
        
    else:
        return False

def get_movie(conn,tt):
    """
    Select all the information currently in the database on that certain movie and 
    update element based on movie tt
    """     
    curs=dbi.dict_cursor(conn)

    curs.execute("""
                select * from movie where tt=%s
                """,[tt])
    return curs.fetchone()

def get_director(conn,tt):
    """
    Select all the information currently in the database on the director for a movie 
    based on movie id
    """     
    curs=dbi.dict_cursor(conn)

    curs.execute("""
                select * from movie m join person p on p.nm=m.director where tt=%s;
                """,[tt])
    return curs.fetchone()

def delete_movie(conn,tt):
    """
    Will delete a specified movie form the database
    """
    curs=dbi.dict_cursor(conn)
    curs.execute("""
                    delete from movie where tt=%s
                    """,[tt])
    conn.commit()

def update_movie(conn,title,current_tt,new_tt,release,addedby,director):
    """
    Will update a specified movie form the database
    """
    curs=dbi.dict_cursor(conn)
    curs.execute("""
                    update movie set title=%s,tt=%s,`release`=%s,addedby=%s,director=%s where tt=%s
                    """,[title,new_tt,release,addedby,director,current_tt])
    print("sucessfull insert")
    conn.commit()
    

def check_dups(conn,new_tt):
    """
    Checks Database of duplicates in Movie ID/TT
    """
    curs=dbi.dict_cursor(conn)
    curs.execute("""
                select count(*) from movie where tt=%s
                """,[new_tt])

    found_items=curs.fetchone()
    print(found_items)

    if found_items['count(*)']>0:
        return True
    return False



def select_movies(conn):
    """
    Selects all the movies in the database that are missing information in an column
    that are either missing the director or release date
    """
    curs=dbi.dict_cursor(conn)
    curs.execute("""
                select distinct* from movie where `release` is Null or director is Null 
                """)
    return curs.fetchall()


if __name__ == '__main__':
    dbi.conf("rp104_db")
    conn=dbi.connect()
    test=insert_movie(conn,213,"Little Women",1994)
    
    
