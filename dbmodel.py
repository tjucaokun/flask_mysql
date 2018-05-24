from flask import Flask, request, flash, url_for
from flask_script import Manager

from flask_bootstrap import Bootstrap
from flask import render_template
from flask_sqlalchemy import SQLAlchemy


class Student(db.Model):
    _tablenames_ = 'student'
    id = db.Column(db.BigInteger, nullable=False, primary_key=True)
    name = db.Column(db.String(16), nullable=False)
    sex = db.Column(db.String(16), nullable=False)
    login_year = db.Column(db.Integer, nullable=False)
    login_age = db.Column(db.Integer, nullable=False)
    cla = db.Column(db.Integer, nullable=False)

    def __init__(self, id, sex, name, login_year, login_age, cla):
        self.id = id
        self.name = name
        self.sex = sex
        self.login_age = login_age
        self.login_year = login_year
        self.cla = cla

    def __repr__(self):
        return self


class Course(db.Model):
    _tablenames_ = 'course'
    id = db.Column(db.BigInteger, nullable=False, primary_key=True)
    name = db.Column(db.String(16), nullable=False)
    tea_name = db.Column(db.String(16), nullable=False)
    credit = db.Column(db.Integer, nullable=False)
    adapt_grade = db.Column(db.Integer, nullable=False)
    delete_year = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return self.name

