"""Тренажёр для подготовки к ЕГЭ по русскому языку"""
import datetime
import os
import re
import sqlite3
import sys
from PIL import Image
from random import choice

from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, \
    QInputDialog, QFileDialog
from PyQt5.QtWidgets import QWidget


class Task(QMainWindow, QWidget):
    def __init__(self, list_nt, list_mist, n):
        """
        Класс для отображения окна с текстом задания
        :param list_nt: список со всеми ID вариантов задания n

        :param list_mist: список с ID вариантов задания n, в которых
        пользователь допустил ошибку

        :param n: номер задания, по которому будет проходить тест
        """
        super().__init__()

        self.n = n

        name_of_file = 'main_task_ui.ui'
        uic.loadUi(name_of_file, self)

        self.setWindowTitle(f'Задание №{self.n}')
        self.n_btn.clicked.connect(self.check_rv)

        self.lineEdit.setPlaceholderText('Введите слово')
        self.list_nt = list_nt
        self.list_mist = list_mist
        self.l_of_answers = list()
        self.l_of_id = list()

        # удаляем повторения из списка list_nt
        for i in self.list_nt:
            if i in self.list_mist:
                self.list_nt.remove(i)

        self.counter = 0
        self.counter_right_var = 0

        self.test_t()

    def test_t(self):
        self.counter += 1

        # номера заданий сначала выбераем из list_mist, если в нём
        # закончились варианты, то добавляем из list_nt
        if len(self.list_mist) == 0:
            self.list_mist.extend(self.list_nt)

        self.id = choice(self.list_mist)
        self.list_mist.remove(self.id)

        # вызываем метод для вставки текста 10 раз
        if self.counter % 11 != 0:
            self.st_t()
        else:
            self.resuit_w = Res(self.counter_right_var, self.counter,
                                self.l_of_answers, self.l_of_id,
                                self.n)
            self.resuit_w.show()
            self.hide()

            # обновляем статистику по заданиям
            res = cur.execute(
                f'''select res_t from statistics 
                where n = {int(self.n)}''').fetchall()
            cur.execute(
                f'update statistics set res_t = '
                f'{res[0][0] + 10} where n = {int(self.n)}')
            res = cur.execute(
                f'''select right_t from statistics 
                where n = {int(self.n)}''').fetchall()
            cur.execute(
                f'update statistics set right_t = '
                f'{res[0][0] + self.counter_right_var} '
                f'where n = {int(self.n)}')
            res = cur.execute(
                '''select res_t from statistics 
                where n = 1''').fetchall()
            cur.execute(
                f'update statistics set res_t = '
                f'{res[0][0] + 10} where n = 1')
            res = cur.execute(
                '''select right_t from statistics 
                where n = 1''').fetchall()
            cur.execute(
                f'update statistics set right_t = '
                f'{res[0][0] + self.counter_right_var} where n = 1')
            con.commit()

    def check_rv(self):
        """Проверям верность данного пользователем ответа"""
        self.rv = cur.execute(
            f'''select right_var from 
            task_{self.n} where id = 
            {self.id}''').fetchall()
        if self.lineEdit.text().lower() == self.rv[0][0]:
            cur.execute(
                f'update task_{self.n} set mistake = 0 '
                f'where id = {self.id}')
            con.commit()
            self.counter_right_var += 1
        else:
            cur.execute(
                f'update task_{self.n} set mistake = 1'
                f' where id = {self.id}')
            con.commit()
        self.l_of_answers.append(
            [self.lineEdit.text().lower(), self.rv[0][0]])
        self.l_of_id.append(self.id)

        self.lineEdit.clear()
        self.test_t()

    def st_t(self):
        """Вставляем в окно текст"""
        self.label_id.setText(str(self.id))

        self.task_dir = cur.execute(f'''select  var from 
                                task_{self.n} where id = 
                                {self.id}''').fetchall()

        self.task = Image.open(f'{self.task_dir[0][0]}').resize(
            (605, 340))
        self.task.save(self.task_dir[0][0])

        self.task = QPixmap(self.task_dir[0][0])

        self.main_label.setPixmap(self.task)

        self.lineEdit.setFocus()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "Сообщение",
            "Вы действительно хотите выйти? В случае выхода "
            "результаты"
            " данного тестирования никак не отразятся на статистике.",
            QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
            ex.show()
        else:
            event.ignore()


class Res(QMainWindow, QWidget):
    def __init__(self, counter_right_var, counter, l_of_answers,
                 l_of_id, n):
        """
        Класс для отображения окна с результатом
        :param counter_right_var: счётчик верных ответов
        :param counter: счётчик ответов данных пользователем
        :param l_of_answers: список ответов данных пользователем в
        ходе тестирования
        :param l_of_id: список ID заданий, по которым пользователь
        проходил тесстирование
        :param n: номер задания по которому пользователь проходил тест
        """
        super().__init__()

        self.counter_right_var = counter_right_var
        self.counter = counter
        self.l_of_answers = l_of_answers
        self.l_of_id = l_of_id
        self.n = n

        uic.loadUi('res_des.ui', self)
        self.setWindowTitle('Результат')
        self.res_label.setText(
            f'{self.counter_right_var} / {self.counter - 1}')

        self.labels = [[self.res_1u, self.res_1r],
                       [self.res_2u, self.res_2r],
                       [self.res_3u, self.res_3r],
                       [self.res_4u, self.res_4r],
                       [self.res_5u, self.res_5r],
                       [self.res_6u, self.res_6r],
                       [self.res_7u, self.res_7r],
                       [self.res_8u, self.res_8r],
                       [self.res_9u, self.res_9r],
                       [self.res_10u, self.res_10r]]

        indexcounter_main = 0
        indexcounter_sub = 0

        for element in self.labels:
            for elem in element:
                elem.setText(str(self.l_of_answers[indexcounter_main][
                                     indexcounter_sub]))
                indexcounter_sub += 1
            if self.labels[indexcounter_main][
                indexcounter_sub - 1].text() == \
                    self.labels[indexcounter_main][
                        indexcounter_sub - 2].text():
                self.labels[indexcounter_main][
                    indexcounter_sub - 2].setStyleSheet(
                    "background-color: green;")
                self.labels[indexcounter_main][
                    indexcounter_sub - 1].setStyleSheet(
                    "background-color: green;")
            else:
                self.labels[indexcounter_main][
                    indexcounter_sub - 2].setStyleSheet(
                    "background-color: red;")
                self.labels[indexcounter_main][
                    indexcounter_sub - 1].setStyleSheet(
                    "background-color: red;")
            indexcounter_main += 1
            indexcounter_sub = 0

        if self.counter_right_var <= 5:
            self.pixmap = QPixmap('fail2.jpg')
            self.label.setPixmap(self.pixmap)
            self.label.move(30, 150)
        else:
            self.pixmap = QPixmap('gatsby.jpg')
            self.label.setPixmap(self.pixmap)
            self.label.move(100, 150)
        # вставляем картинку в соответствии с результатом
        # пользователеля

        self.pushButton.clicked.connect(self.func_close)
        self.resb_1.clicked.connect(self.exp)
        self.resb_2.clicked.connect(self.exp)
        self.resb_3.clicked.connect(self.exp)
        self.resb_4.clicked.connect(self.exp)
        self.resb_5.clicked.connect(self.exp)
        self.resb_6.clicked.connect(self.exp)
        self.resb_7.clicked.connect(self.exp)
        self.resb_8.clicked.connect(self.exp)
        self.resb_9.clicked.connect(self.exp)
        self.resb_10.clicked.connect(self.exp)

    def exp(self):
        self.expl = Explanation(self.l_of_id, self.n)
        self.expl.show()
        # отображаем объяснение к заданию

    def func_close(self):
        self.close()
        self.l_of_answers.clear()
        self.l_of_id.clear()
        ex.show()

    def closeEvent(self, event):
        self.func_close()


class Explanation(QMainWindow, QWidget):
    def __init__(self, l_of_id, n):
        """
        Класс для отображения окна с объяснением
        :param l_of_id: список ID заданий, по которым пользователь
        проходил тесстирование
        :param n: номер задания по которому пользователь проходил тест
        """
        super().__init__()

        uic.loadUi('explanation.ui', self)
        self.setWindowTitle('Пояснение')

        self.l_of_id = l_of_id
        self.n = n
        self.ind_n = int(self.sender().text().split()[-1]) - 1
        self.n_of_task = self.l_of_id[self.ind_n]
        self.expl_dir = cur.execute(
            f'''select explanation from task_{n} 
            where id = {self.n_of_task}''').fetchall()
        self.expl = Image.open(f'{self.expl_dir[0][0]}').resize(
            (605, 340))
        self.expl.save(self.expl_dir[0][0])
        self.expl = QPixmap(self.expl_dir[0][0])
        self.label.setPixmap(self.expl)

    def func_close(self):
        self.close()

    def closeEvent(self, event):
        self.func_close()


class Adder(QMainWindow, QWidget):
    def __init__(self):
        super().__init__()

        uic.loadUi('adder.ui', self)
        self.setWindowTitle('Добавление задания')
        self.task_fname, self.expl_fname = '', ''
        self.pushButton_add.clicked.connect(self.add_task)
        self.task_add.clicked.connect(self.choose_task_img)
        self.expl_add.clicked.connect(self.choose_expl_img)

    def add_task(self):
        if not (self.n_le.text() and
                self.rv_le.text() and
                self.task_fname and
                self.expl_fname):
            QMessageBox.critical(self, "Ошибка ",
                                 "Пропущена одна из граф, "
                                 "сохранение задания не "
                                 "было выполнено",
                                 QMessageBox.Ok)
        # проверяем заполненность всех граф
        elif int(self.n_le.text()) not in [4, 7, 9, 10, 11, 12, 13,
                                           14, 15]:
            QMessageBox.critical(self, "Ошибка ",
                                 "Неверно введён номер задания",
                                 QMessageBox.Ok)
        else:
            n = self.n_le.text()
            rs = cur.execute(f'''select id 
            from task_{n}''').fetchall()[-1][0] + 1
            cur.execute(f"""insert into task_{n} (id,
            right_var,
            var,
            mistake,
            explanation)
             values({int(rs)},
                    '{self.rv_le.text()}',
                    '{self.task_fname}',
                    0,
                    '{self.expl_fname}')""")
        con.commit()

        self.hide()
        ex.show()

    def choose_task_img(self):
        self.task_fname = QFileDialog.getOpenFileName(
            self, 'Выберете изображение с текстом задания', '',
            'Картинка (*.jpg);')[0]
        if self.task_fname:
            self.task_add.setEnabled(False)

    def choose_expl_img(self):
        self.expl_fname = QFileDialog.getOpenFileName(
            self, 'Выберете изображение с объяснением к заданию', '',
            'Картинка (*.jpg);')[0]
        if self.expl_fname:
            self.expl_add.setEnabled(False)

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "Сообщение",
            "Вы действительно хотите выйти? В случае выхода "
            "без сохранения вопроса, "
            "вопрос не будет добавлен в базу вопросов.",
            QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
            ex.show()
        else:
            event.ignore()


class Application(QMainWindow, QWidget):
    """Класс для отображения главного окна"""

    def __init__(self):
        super().__init__()
        uic.loadUi('main_des_updated.ui', self)
        self.setWindowTitle(
            'Тренажёр для подготовки к ЕГЭ по русскому языку')
        self.task_4.clicked.connect(self.start_task)
        self.task_7.clicked.connect(self.start_task)
        self.task_9.clicked.connect(self.start_task)
        self.task_10.clicked.connect(self.start_task)
        self.task_11.clicked.connect(self.start_task)
        self.task_12.clicked.connect(self.start_task)
        self.task_13.clicked.connect(self.start_task)
        self.task_14.clicked.connect(self.start_task)
        self.task_15.clicked.connect(self.start_task)
        self.action.triggered.connect(self.upload_stat)
        self.action_2.triggered.connect(self.stat_to_zero)
        self.action_3.triggered.connect(self.add_a_task)
        self.action_4.triggered.connect(self.delete_a_task)

    def start_task(self):
        self.n = self.sender().text().split()[-1]

        self.list_nt = []
        for i in cur.execute(
                f'select id from task_{self.n}').fetchall():
            self.list_nt.append(*i)

        self.list_mist = []
        for i in cur.execute(
                f'select id from task_{self.n} '
                f'where mistake = 1').fetchall():
            self.list_mist.append(*i)

        self.task = Task(self.list_nt, self.list_mist, self.n)
        self.task.show()
        self.hide()

    def upload_stat(self):
        name_of_file, ok = QInputDialog.getText(self, 'Сообщение',
                                                'Введите имя файла, в'
                                                ' котором будет '
                                                'сохранена статистика'
                                                '(название файла без '
                                                'знаков препинания и '
                                                'расширений):')
        flag = bool(re.search(r'^[A-Za-zА-Яа-я1234567890]{1,999999}$',
                              name_of_file))
        # проверяем допустимость названия файла
        if ok and flag:
            file = open(name_of_file + '.txt', encoding='utf-8',
                        mode='w')

            file.write(
                f'Время выгрузки статистики: '
                f'{datetime.datetime.now()}\n')

            for i in range(1, 11):
                t_res = cur.execute(
                    f'''select id_t, right_t, res_t from statistics
                     where i = {i}''').fetchall()
                t_res = str(t_res[0][0]) + ' ' + str(
                    t_res[0][1]) + '/' + str(t_res[0][2]) + '\n'
                file.write(t_res)

            file.close()

            # открываем файл со статистикой для удобства
            os.startfile(name_of_file + '.txt', "open")

            reply = QMessageBox.question(
                self, "Сообщение",
                'Желаете распечатать файл с статистикой?',
                QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                # шлём файл на печать
                os.startfile(name_of_file + '.txt', "print")
        elif not ok:
            pass
        elif not flag:
            QMessageBox.critical(self, "Ошибка ",
                                 "Неверный формат названия("
                                 "присутствуют недопустимые символы)",
                                 QMessageBox.Ok)

    def stat_to_zero(self):
        for i in range(1, 11):
            cur.execute(
                f'''update statistics set right_t = 0, 
                res_t = 0 where i = {i}''')
        con.commit()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "Сообщение",
            "Вы действительно хотите выйти?",
            QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def add_a_task(self):
        # отображаем окно для добавления заданий
        self.adder = Adder()
        self.adder.show()
        self.hide()

    def delete_a_task(self):
        que, ok = QInputDialog.getText(self, 'Сообщение',
                                       'Введите вариант '
                                       'задания, который вы '
                                       'хотите удалить в '
                                       'формате "номер '
                                       'задания / идентифика'
                                       'ционный номер вариан'
                                       'та" (например: 9/1)')
        que = que.split('/')
        if ok:
            rs = len(cur.execute(
                f'''select id from task_{int(que[0])}''').fetchall())
            if rs <= 10:
                QMessageBox.critical(self, "Критическая ошибка",
                                     "Удаление недопустимо",
                                     QMessageBox.Ok)
            elif int(que[0]) not in [4, 7, 9, 10, 11, 12, 13,
                                     14, 15]:
                QMessageBox.critical(self, "Ошибка ",
                                     "Неверно введён номер задания",
                                     QMessageBox.Ok)
            elif not que[1].isdigit():
                QMessageBox.critical(self, "Ошибка ",
                                     "Неверно введён номер задания",
                                     QMessageBox.Ok)
            else:
                cur.execute(f'''delete from task_{que[0]} 
                where id == {int(que[1])}''')
                con.commit()
        elif not ok:
            pass


# устанавливаем соединение с БД
con = sqlite3.connect('tester_rebuild_database.db')
cur = con.cursor()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Application()
    ex.show()
    sys.exit(app.exec())
