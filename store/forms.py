from django import forms
from .models import Product
from .widgets import SimpleListWidget


DEFAULT_CARE_INSTRUCTIONS = """
<h4>Загальні рекомендації по догляду за шкіряними виробами:</h4>
<ul>
    <li>Уникайте тривалого контакту з водою — краще швидко витирати вологу.</li>
    <li>Зберігайте вироби при кімнатній температурі, уникаючи високої вологості.</li>
    <li>Для очищення використовуйте спеціальні м’які засоби для шкіри.</li>
    <li>Регулярно обробляйте кремами або бальзамами для збереження м’якості та еластичності.</li>
    <li>Уникайте тривалого перебування на прямому сонці.</li>
    <li>Обережно ставтесь до гострих предметів, щоб не подряпати поверхню.</li>
</ul>
"""

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'sizes': SimpleListWidget(),
            'colors': SimpleListWidget(),
            'features': SimpleListWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk or not self.instance.care_instructions:
            self.fields['care_instructions'].initial = DEFAULT_CARE_INSTRUCTIONS

