# Zadanie

W oparciu o framework Django, napisać prosty moduł, generujący tzw. „admin panel” na wzór domyślnego, dostępnego w Django. Interfejs powinien być możliwie prosty i minimalistyczny. Moduł powinien spełniać następujące wymogi: 
- Możliwość dodania modelu do admin panelu 
- Widok z listą modeli do niego dodanych 
- Widok wszystkich obiektów danego modelu (List View) 
- Możliwość dodania, aktualizacji, usunięcia obiektu (Create, Update, Delete View) 
- Wszystkie widoki, wraz z odpowiadającymi im adresami url, powinny być generowane automatycznie 
- Wpięcie wtyczki pod dowolny, wybrany przez użytkownika, root url 
- Dostęp do admin panelu powinien być ograniczony do użytkowników z odpowiednimi uprawnieniami

Wedle uznania widoki mogą udostępniać API(Django REST Framework) lub być renderowane do HTML.
