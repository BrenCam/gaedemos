import os
import cgi
import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template

# These are used for linking/ordering

class Books(db.Model):
    notes = db.StringProperty(required=False)

class Libraries(db.Model):
    notes = db.StringProperty(required=False)
     
# Data models
class Library(db.Model):
    name = db.StringProperty(required=True)
    address = db.StringProperty(required=True)
    city = db.StringProperty(required=True)
    library_list = db.ReferenceProperty(Libraries,
        required=True, collection_name='ref_libs')
    
class Book(db.Model):
    title = db.StringProperty(required=True)
    author = db.StringProperty(required=True)
    library = db.ReferenceProperty(Library,
        required=True, collection_name='books')
    book_list = db.ReferenceProperty(Books,
        required=True, collection_name='ref_books')

class MainPage(webapp.RequestHandler):
  def get(self):

    # Library collection
    libs = Libraries()
    libs.put()
    
    # Books collection
    books = Books()
    books.put()
    
    # Setup libraries
    lib1 = Library(name='lib1', address='street a', city='city1',
        library_list=libs)
    lib2 = Library(name='lib2', address='street b', city='city2',
        library_list=libs)
    lib1.put()
    lib2.put()
    
    # Books:
    #   Both libraries
    book1 = Book(title='book1', author='author one', 
        library=lib1, book_list=books)
    book2 = Book(title='book1', author='author one',
        library=lib2, book_list=books)
    #   Only first library
    book3 = Book(title='book2', author='author one',
        library=lib1, book_list=books)
    #   Both libraries
    book4 = Book(title='book3', author='author two',
        library=lib1, book_list=books)
    book5 = Book(title='book3', author='author two',
        library=lib2, book_list=books)
    book1.put()
    book2.put()
    book3.put()
    book4.put()
    book5.put()


    libs_books = libs.ref_libs.order('name')
    
    books_libs = books.ref_books.order('author').order('-title')
  
    template_values = {
        'libs_books': libs_books,
        'books_libs': books_libs
      }

    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

    
def main():
    application = webapp.WSGIApplication(
                                       [('/', MainPage)],
                                       debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()
