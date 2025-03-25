# Asystent Anonimizacji Danych Osobowych

## Opis
Asystent Anonimizacji Danych Osobowych to aplikacja zgodna z wymogami RODO, stworzona w celu automatycznego wykrywania i anonimizacji danych osobowych w tekstach. Aplikacja wykorzystuje zaawansowane techniki przetwarzania języka naturalnego (NLP) oraz wyrażenia regularne do identyfikacji i maskowania wrażliwych informacji.

## Funkcje
- **Automatyczne wykrywanie** różnych rodzajów danych osobowych:
  - Imiona i nazwiska osób
  - Lokalizacje (miasta, adresy)
  - Nazwy organizacji
  - Numery telefonów
  - Adresy e-mail
  - Daty urodzenia
  - Numery PESEL
  - Numery kont bankowych
  - Kody pocztowe
  - Numery polis ubezpieczeniowych
  - Numery dowodów osobistych
  - Numery budynków

- **Intuicyjny interfejs graficzny** z funkcjami:
  - Wczytywanie tekstu z pliku
  - Zapisywanie zanonimizowanego tekstu do pliku
  - Wyświetlanie szczegółowego podsumowania wykrytych danych osobowych
  - Wyróżnianie zanonimizowanych danych kolorowym tłem dla łatwej identyfikacji

## Wymagania systemowe
- Python 3.12 lub nowszy
- Zainstalowane biblioteki:
  - tkinter (zazwyczaj dołączony do standardowej instalacji Pythona)
  - transformers
  - pytorch

## Instalacja
1. Sklonuj lub pobierz repozytorium na swój komputer
2. Zainstaluj wymagane biblioteki:
```
pip install transformers torch
```
3. Uruchom aplikację:
```
python main.py
```

## Jak korzystać z aplikacji
1. **Wprowadź tekst do anonimizacji**:
   - Wpisz tekst bezpośrednio w górne pole tekstowe, lub
   - Kliknij przycisk "Wczytaj z pliku" aby zaimportować tekst z pliku TXT

2. **Anonimizuj dane**:
   - Kliknij przycisk "Anonimizuj"
   - Aplikacja przeanalizuje tekst i zastąpi dane osobowe odpowiednimi znacznikami

3. **Przejrzyj wyniki**:
   - Zanonimizowany tekst pojawi się w dolnym polu
   - Dane osobowe będą zastąpione znacznikami takimi jak <PERSON>, <LOCATION>, itp.
   - Znaczniki będą wyróżnione kolorowym tłem dla łatwej identyfikacji

4. **Analiza statystyk**:
   - Kliknij przycisk "Pokaż szczegóły" aby zobaczyć podsumowanie wykrytych danych
   - W oknie statystyk zobaczysz liczbę wykrytych danych według kategorii

5. **Zapisz wyniki**:
   - Kliknij przycisk "Zapisz do pliku" aby zapisać zanonimizowany tekst do pliku TXT

## Technologia
Aplikacja łączy dwie główne metody wykrywania danych osobowych:
1. **AI/NLP** - wykorzystuje model HerBERT, dostosowany do języka polskiego, do rozpoznawania nazw własnych (NER)
2. **Wyrażenia regularne** - wykrywa ustrukturyzowane dane, takie jak numery telefonów, PESEL, kody pocztowe, itp.

## Uwagi
- Aplikacja służy jako narzędzie pomocnicze - zawsze sprawdź zanonimizowany tekst pod kątem ewentualnych pominięć
- Skuteczność anonimizacji zależy od jakości i formatu tekstu wejściowego
- W przypadku dużych tekstów, przetwarzanie może zająć kilka sekund ze względu na użycie modelu AI

## Autorzy
Aplikacja została stworzona jako projekt akademicki w ramach zajęć z etyki w AI.

Weronika Czyż

Damian Wiśniewski

## Licencja
Ten projekt jest udostępniany na licencji MIT.

## Przykładowy tekst do testów
Poniżej znajduje się przykładowy tekst, który możesz skopiować i wkleić do aplikacji, aby przetestować funkcję anonimizacji:

```
Jan Kowalski, urodzony 15.05.1985, mieszka przy ul. Wiosennej 10, 00-001 Warszawa.
Jego numer PESEL to 85051512345, a dowód osobisty ma numer ABC123456.
Kontakt z nim możliwy jest poprzez adres e-mail jan.kowalski@example.com.
Telefon kontaktowy to +48 600 123 456, co stanowi część wrażliwych danych.
Zatrudniony jest w firmie TestSp. na stanowisku kierownika działu IT, z wynagrodzeniem 8000 PLN brutto.
Informacje o jego stanie zdrowia, w tym alergii na penicylinę, są przechowywane w systemie medycznym firmy.
W rejestrze znajdują się także dane dotyczące historii ubezpieczeniowej oraz numer polisy ubezpieczeniowej PL123456789.
Jego małżonka, Anna Nowak, urodzona 20.03.1987, posiada numer PESEL 87032054321 i mieszka razem z nim.
W bazie danych firmy zapisano również informacje o numerze konta bankowego 12 3456 7890 1234 5678 9012 3456.
Dane te są objęte rygorystycznymi procedurami RODO, aby zapewnić ich ochronę przed nieuprawnionym dostępem.
```

Ten tekst zawiera różne rodzaje danych osobowych, które aplikacja powinna poprawnie wykryć i zanonimizować. 