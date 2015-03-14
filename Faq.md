# FormAlchemy Frequently Asked Questions #

## 0.3 ##

No FAQs yet.

## 0.2 ##

**Why are my fields filled with '<sqlalchemy.orm.attributes.InstrumentedAttribute object at 0xaa1356c>' or 'Property(col, <class 'project.model.mymodel.Class'>)' rather than the actual value?**

Because you are probably passing an uninstantiated class. Make sure you instantiate your !SQLAlchemy class before passing it to FormAlchemy.