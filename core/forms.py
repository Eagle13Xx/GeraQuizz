from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    """
    Um formulário de criação de usuário personalizado que inclui
    validação de email (obrigatório e único).
    """

    email = forms.EmailField(
        required=True,
        help_text="Obrigatório. Um email válido.",
        widget=forms.EmailInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-blue focus:border-primary-blue'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # Define os campos que aparecerão no formulário
        fields = ("username", "email",)

    def __init__(self, *args, **kwargs):
        """
        Sobrescrevemos o init para adicionar classes Tailwind
        aos campos que o UserCreationForm já cria.
        """
        super().__init__(*args, **kwargs)

        # Adiciona classes Tailwind aos campos padrão
        tailwind_class = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-blue focus:border-primary-blue'
        self.fields['username'].widget.attrs.update({'class': tailwind_class})
        self.fields['password1'].widget.attrs.update({'class': tailwind_class})
        self.fields['password2'].widget.attrs.update({'class': tailwind_class, 'aria-label': 'Confirmação de senha'})

    def clean_email(self):
        """
        Validação de email: Garante que o email ainda não foi cadastrado.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este endereço de e-mail já está em uso.")
        return email

    def save(self, commit=True):
        """
        Salva o usuário e também o campo de email.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user