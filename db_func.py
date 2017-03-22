import sqlite3
import os
import sys


class DataBaseHuaban:
    def __init__(self):
        self.init_flag = False
        self.sql_count = 0
        self.set_max_buf_sql_cnt = 200
        pass

    def load(self, db_file_path):
        if not os.path.exists(db_file_path):
            self.dbHandle = self.init_db(db_file_path)
        else:
            self.dbHandle = sqlite3.connect(db_file_path)
        self.dbHandle.text_factory = str
        self.init_flag = True
        pass

    def init_db(self, db_file_path):
        db_handle = sqlite3.connect(db_file_path)
        db_handle.execute('CREATE TABLE hash_record(\
          file_url TEXT ,\
          board_code INT ,\
          description TEXT ,\
          file_size INT,\
          is_done INT)')
        db_handle.commit()
        db_handle.execute('CREATE INDEX hash_record_index on hash_record(full_file_path, hash_code)')

        db_handle.execute('CREATE TABLE scan_record(\
          folder_path TEXT PRIMARY KEY ,\
          depth INT ,\
          scan_time DATETIME,\
          state INT)')
        db_handle.commit()
        db_handle.execute('CREATE INDEX scan_record_index on scan_record(folder_path)')

        db_handle.commit()
        return db_handle
        pass

    def store_file_record(self, full_file_path, hash_code, description=None):
        if not self.init_flag:
            self.err_output('load db first')
            return
        if 'nt' == os.name:
            full_file_path = unicode(full_file_path.decode('gbk'))
        try:
            dup_file_list = self.check_hash_dup(full_file_path, hash_code)
            dup_file_list = list()
            same_count = len(dup_file_list)
            if same_count != 0:
                same_count += 1
            for dup_file_path in dup_file_list:
                self.update_file_same_count(dup_file_path, same_count)
            stat = os.stat(full_file_path)
            file_size = stat.st_size
            self.dbHandle.execute('INSERT OR REPLACE INTO hash_record VALUES (?,?,?,?,?)',
                                (full_file_path, hash_code, description, file_size, same_count))
        except sqlite3.DataError:
            self.err_output('DataError')
            return
        self.sql_count += 1
        if self.sql_count >= self.set_max_buf_sql_cnt:
            self.sql_count = 0
            self.dbHandle.commit()
        pass

    def update_file_same_count(self, file_path, same_count):
        self.dbHandle.execute('update hash_record set same_count = (?) \
                                where hash_record.full_file_path == (?)',
                              (same_count, file_path))
        self.dbHandle.commit()
        pass

    def do_commit(self):
        if self.sql_count > 0:
            self.dbHandle.commit ()
        pass

    def check_hash_dup(self, file_path, hash_code):
        dup_file_list = list()
        con = self.dbHandle.execute('select * from hash_record where hash_record.hash_code == (?) \
                                  and hash_record.full_file_path != (?)', (hash_code, file_path))
        if con.rowcount != 0:
            dup_tuple_list = con.fetchall()
            for tuple_row in dup_tuple_list:
                (file_path,_,_,_,_) = tuple_row
                dup_file_list.append(file_path)
                print 'append same [%s]' % file_path.decode('utf-8')
        return dup_file_list

        pass

    # state 0:scanning 1:already scaned
    def store_scan_record(self, full_folder_path, state):
        if not self.init_flag:
            self.err_output('load db first')
            return False
        depth = get_dir_depth(full_folder_path)
        time_now = datetime.datetime.now()
        self.dbHandle.execute('INSERT OR REPLACE INTO scan_record VALUES (?,?,?,?)',
                              (full_folder_path, depth, time_now, state))
        self.dbHandle.commit()
        pass


