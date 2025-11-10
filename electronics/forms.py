from django import forms
from .models import NetworkNode, Contact, Product, Employee


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = '__all__'
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@mail.com'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Россия'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Москва'}),
            'street': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ул. Примерная'}),
            'house_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'д. 10'}),
        }


class NetworkNodeForm(forms.ModelForm):
    class Meta:
        model = NetworkNode
        fields = ['name', 'node_type', 'contact', 'supplier', 'debt']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название узла'}),
            'node_type': forms.Select(attrs={'class': 'form-control'}),
            'contact': forms.Select(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'debt': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Динамически ограничиваем выбор поставщиков
        if self.instance and self.instance.pk:
            if self.instance.node_type == 'factory':
                self.fields['supplier'].queryset = NetworkNode.objects.none()
            elif self.instance.node_type == 'retail':
                self.fields['supplier'].queryset = NetworkNode.objects.filter(node_type='factory')
            elif self.instance.node_type == 'entrepreneur':
                self.fields['supplier'].queryset = NetworkNode.objects.filter(node_type='retail')


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'release_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }