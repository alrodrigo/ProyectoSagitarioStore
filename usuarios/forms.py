from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Apellido'})
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Correo electrónico'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar contraseña'})
    )
    terms = forms.BooleanField(
        required=True,
        error_messages={'required': 'Debes aceptar los términos y condiciones'}
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Usar el email como username
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Correo electrónico'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'})
    )
    remember_me = forms.BooleanField(required=False)

    error_messages = {
        'invalid_login': 'Por favor ingresa un correo electrónico y contraseña correctos.',
        'inactive': 'Esta cuenta está inactiva.',
    }

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # Intentar encontrar el usuario por email
            try:
                user = User.objects.get(email=username)
                # Si encontramos el usuario, intentamos autenticarlo con su username real
                self.user_cache = authenticate(username=user.username, password=password)
                if self.user_cache is None:
                    raise forms.ValidationError(
                        self.error_messages['invalid_login'],
                        code='invalid_login'
                    )
                elif not self.user_cache.is_active:
                    raise forms.ValidationError(
                        self.error_messages['inactive'],
                        code='inactive',
                    )
            except User.DoesNotExist:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login'
                )
        return self.cleaned_data