from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required, login_required
import datetime

from .models import Book, Author, BookInstance, Genre
from .forms import RenewBookForm

def index(request):
    word = "Warcraft"
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()
    num_genres = Genre.objects.count()
    num_books_containing_word = Book.objects.filter(title__icontains=word).count()

    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    return render(
        request,
        'index.html',
        context = {
            'num_books': num_books,
            'num_instances': num_instances,
            'num_instances_available': num_instances_available,
            'num_authors': num_authors,
            'num_genres': num_genres,
            'word': word,
            'num_books_containing_word': num_books_containing_word,
            'num_visits': num_visits
        },
    )

class BookListView(generic.ListView):
    model = Book
    template_name = 'books/book_list.html'
    paginate_by = 10

class BookDetailView(generic.DetailView):
    model = Book
    template_name = 'books/book_detail.html'

class AuthorListView(generic.ListView):
    model = Author
    template_name = 'authors/author_list.html'
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    model = Author
    template_name = 'authors/author_detail.html'

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class LoanedBooksForLibrariansListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name = 'catalog/bookinstance_list_for_librarians.html'
    paginate_by = 10

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_inst = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form = RenewBookForm(request.POST)

        if form.is_valid():
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()
            return HttpResponseRedirect(reverse('all-borrowed'))

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date':proposed_renewal_date})

    return render(request, 'catalog/book_renew_librarian.html', {'form':form, 'book_inst':book_inst})

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author

class AuthorCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.can_edit_author'
    model = Author
    fields = '__all__'
    initial = {'date_of_death' : datetime.date.today()}

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_edit_author'
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_edit_author'
    model = Author
    success_url = reverse_lazy('authors')

class BookCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.can_edit_book'
    model = Book
    fields = '__all__'

class BookUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_edit_book'
    model = Book
    fields = '__all__'
    
class BookDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_edit_book'
    model = Book
    success_url = reverse_lazy('books')