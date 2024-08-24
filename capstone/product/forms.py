from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'rating_count', 'avg_rating',
                  'reviews_count', 'reviews', 'quantity']
        widgets = {
            'reviews': forms.Textarea(attrs={'rows': 12, 'cols': 50}),
            'avg_rating': forms.NumberInput(attrs={'placeholder': 'Average Rating', 'step': '0.01'}),
            'rating_count': forms.NumberInput(attrs={'placeholder': 'Rating Count'}),
            'reviews_count': forms.NumberInput(attrs={'placeholder': 'Total Reviews'}),
            'quantity': forms.NumberInput(attrs={'placeholder': 'Product Quantity'}),
            'title': forms.TextInput(attrs={'placeholder': 'Product Title'}),
        }

    def __init__(self, *args, **kwargs):
        # Ensure that no initial data is set unless explicitly provided
        initial_data = kwargs.get('initial', {})
        if not initial_data:
            kwargs['initial'] = {field: '' for field in self.Meta.fields}

        super(ProductForm, self).__init__(*args, **kwargs)
        # # Make all fields required
        for field in self.fields:
            self.fields[field].required = True
