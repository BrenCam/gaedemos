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
        
# Classes to link images to tags
# Classes for the collections
class Images(db.Model):
    dummy = db.StringProperty(required=False)

class Tags(db.Model):
    dummy = db.StringProperty(required=False)
        
class Image(db.Model):
    """ Image has many tags """
    #~ title = db.StringProperty(required=True)
    title = db.StringProperty()
    imgscol = db.ReferenceProperty(Images, collection_name='imgscol')
    
    # provide list of associated tags
    def tags(self):
        return (x.tag for x in self.imagetag_set)

class Tag(db.Model):
    """ Tag can apply to many images """
    #~ name= db.StringProperty(required=True)
    name= db.StringProperty()
    tagscol = db.ReferenceProperty(Tags, collection_name='tagscol')

    def images(self):
        return (x.image for x in self.imagetag_set)

# Here's the magic 
# Create class to mimic intersect table
class ImageTag(db.Model):
    """ Class doc """
    
    image = db.Reference(Image)
    tag = db.Reference(Tag)        

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

# handle images
class ImgPage(webapp.RequestHandler):
    
  def get(self):
    #~ self.response.out.write('just testing')
     
    # Image collection
    imgs = Images()
    imgs.put()
    
    # Tags collection
    tags = Tags()
    tags.put()

    # load some test data
    # Setup tags of cities and countries
    # Define tags first - Before referencing
    tagC = Tag(name='City',  tagscol=tags)
    tagE = Tag(name='Europe',  tagscol=tags)
    tagF = Tag(name='France',  tagscol=tags)
    tagG = Tag(name='Germany',  tagscol=tags)
    tagU = Tag(name='UK',  tagscol=tags)
    tagC.put()
    tagE.put()
    tagF.put()
    tagG.put()
    tagU.put()
        
    # Setup images
    imgP = Image(title='Paris', imgscol=imgs)
    imgL = Image(title='London',imgscol=imgs)
    imgM = Image(title='Manchester',imgscol=imgs)
    imgB = Image(title='Berlin',imgscol=imgs)
    imgP.put()
    imgL.put()
    imgM.put()
    imgB.put()

    # Populate tables/models on GAE
    # Assign City and Country Tags to each image
    # note redundant data creation here
    l1 = ImageTag(image=imgP, tag=tagC)
    l2 = ImageTag(image=imgP, tag=tagF)

    l3 = ImageTag(image=imgL, tag=tagC)
    l4 = ImageTag(image=imgL, tag=tagU)
    
    l5 = ImageTag(image=imgM, tag=tagC)
    l6 = ImageTag(image=imgM, tag=tagU)
    
    l7 = ImageTag(image=imgB, tag=tagC)
    l8 = ImageTag(image=imgB, tag=tagG)
    # load in db
    l1.put()
    l2.put()
    l3.put()
    l4.put()
    l5.put()
    l6.put()
    l7.put()
    l8.put()
    
    # pass required objects/collections to view
    
    print '****** imgs: %s' %imgs
    print '****** tags: %s' %tags
    template_values = {
        'imgs_tags': imgs.imgscol.order('title'),
        'tags_imgs': tags.tagscol.order('name')
      }

    path = os.path.join(os.path.dirname(__file__), 'images.html')
    # pass data to the view/template
    
    #~ for item in imgs.imgscol:
        #~ for img in imgs_tags
        #~ self.response.out.write('*title: %s; '  %item.title)
        #~ for tag in item.tags():
            #~ self.response.out.write('tag: %s; '  %tag.name)

    #~ for item in tags.imgscol:
        #~ for img in imgs_tags
        #~ self.response.out.write('*title: %s; '  %item.title)
     #~ 


    self.response.out.write(template.render(path, template_values))    
    
class TestPage(webapp.RequestHandler):
    
  def get(self):
     self.response.out.write('just testing')

       
def main():
    application = webapp.WSGIApplication([
                                       ('/', MainPage),
                                       ('/test', TestPage),
                                       ('/img', ImgPage)
                                       ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)
    

if __name__ == "__main__":
    main()
