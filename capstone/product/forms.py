from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'ref_id', 'brand', 'manufacture',
                  'categories']  # Fields from the Product model
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Product Title'}),
            'ref_id': forms.TextInput(attrs={'placeholder': 'Reference ID'}),
            'brand': forms.TextInput(attrs={'placeholder': 'Brand'}),
            'manufacture': forms.TextInput(attrs={'placeholder': 'Manufacture Date'}),
            'categories': forms.SelectMultiple(attrs={'placeholder': 'Categories'}),
        }

    def __init__(self, *args, **kwargs):
        # Ensure that no initial data is set unless explicitly provided
        initial_data = kwargs.get('initial', {})
        if not initial_data:
            kwargs['initial'] = {field: '' for field in self.Meta.fields}

        super(ProductForm, self).__init__(*args, **kwargs)
        # Make all fields required
        for field in self.fields:
            self.fields[field].required = True
