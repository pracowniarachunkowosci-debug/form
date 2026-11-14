# SSL stagingu — kontrola PEM i import tylko po akceptacji

Dotyczy **test.pracowniaform.com / vhost 1711054 / serwer533947**. Nie dotyczy apex, `www`, innych vhostów ani FTPS. **14.11.2026: zatwierdzony DNS-01 zakończony, PEM zweryfikowane; po odrębnej zgodzie właściciela importer LH przyjął zestaw i wyświetlił „Włączono własny certyfikat SSL dla domeny test.pracowniaform.com”.** Wartość wyzwania i materiały kluczy pozostają poza repo i komentarzami. [Wynik bieżący](LH_SSL_RESULT_20261114.md).

## 1. Co sprawdzono niezależnie o imporcie LH

Ponownie obejrzano formularz „Własny” dokładnie tego vhosta: oddzielne pola certyfikat / klucz prywatny / CA; brak pola `www` i brak widocznego żądania dodatkowego SAN. Formularz anulowano pusty, bez zapisu. [Oficjalna instrukcja importu](https://www.lh.pl/pomoc/docs/jak-przeniesc-certyfikat-ssl-na-nowy-serwer-w-lh-pl/) opisuje import PEM, ale mówi ogólnie o domenie z i bez `www` oraz używa przykładu certyfikatu komercyjnego. **Nie potwierdza jednoznacznie backendowej akceptacji zewnętrznego LE z jednym SAN dla tego pakietu.**

Wniosek przed zapisem: sam formularz nie wystarczał do deklaracji PASS single-SAN. Następnie wykonano zatwierdzoną próbę: **LH faktycznie przyjęło zewnętrzny LE z jednym SAN, bez `www.test`**. Nie dodano tej nazwy do DNS ani certyfikatu. Akceptacja importera jest osobnym dowodem od kontroli publicznego HTTPS, opisanej w raporcie wyniku.

## 2. Zestaw po pozytywnej walidacji DNS-01

WACS wyeksportował poniższy podstawowy zestaw oraz dodatkowe `chain-full.pem` / `chain-only-full.pem`. Do LH użyto wyłącznie trzech wskazanych pól:

| Plik | Znaczenie / pole LH |
| --- | --- |
| `test.pracowniaform.com-crt.pem` | Jeden leaf → **Certyfikat** |
| `test.pracowniaform.com-key.pem` | Jego prywatny klucz → **Klucz prywatny** |
| `test.pracowniaform.com-chain-only.pem` | Same pośrednie CA, w kolejności → **Klucze CA (pośrednie)** |
| `test.pracowniaform.com-chain.pem` | Leaf + pośrednie; pomocnicza kontrola, **nie** trzecie pole LH |

Dokładne nazwy potwierdzić po eksporcie; nie przepisywać plików ani nie sklejać klucza z certyfikatem. Weryfikacja tylko lokalnie, bez instalowania nowego zaufanego CA w Windows. Anchory zaufania pobrać osobno z [oficjalnych certyfikatów LE](https://letsencrypt.org/certificates/) i sprawdzić tożsamość/fingerprint; nie używać leaf lub chain-only jako trust store. Klucze i kopie zachować w prywatnym katalogu ACL operator/SYSTEM poza repo.

[Walidator](../scripts/check_lh_pem.py) wymaga OpenSSL 3 i nie robi żadnych połączeń sieciowych ani importu:

```powershell
python scripts/check_lh_pem.py --openssl '<OpenSSL3>' `
  --leaf '<PRIVATE>/pem/test.pracowniaform.com-crt.pem' `
  --key '<PRIVATE>/pem/test.pracowniaform.com-key.pem' `
  --chain '<PRIVATE>/pem/test.pracowniaform.com-chain-only.pem' `
  --fullchain '<PRIVATE>/pem/test.pracowniaform.com-chain.pem' `
  --roots '<PRIVATE>/trusted-isrg-roots.pem'
```

Wymagania PASS: dokładnie jeden SAN równy stagingowi; zgodne publiczne klucze leaf/private key (działa dla RSA i EC); brak leaf/duplikatów/root w chain-only; poprawna kolejność pośrednich; fullchain równy leaf+chain-only; zaufany łańcuch, przeznaczenie sslserver i hostname, aktualne daty oraz minimum 30 dni ważności. JSON wyjściowy zawiera fingerprint i publiczne daty, bez prywatnego klucza i ścieżek. Nie jest dowodem instalacji na LH. Nie drukować stderr narzędzi operujących na sekretach do raportu.

## 3. Checklista ręcznego importu — wymaga osobnej zgody

1. Przedstawić właścicielowi wynik weryfikacji PEM: jeden SAN, issuer, notBefore/notAfter, SHA-256 i przypisanie trzech pól. Uzyskać zgodę na **ten certyfikat w vhoście 1711054**. Zgoda na TXT nie obejmuje importu.
2. Ponownie odczytać adres vhosta, serwer i bieżący SSL. Jeżeli pojawił się inny certyfikat lub zmiana zasobu, nie nadpisywać go bez wyjaśnienia. Obecnie brak SSL, więc nie ma certyfikatu stagingu do kopii; nie dotykać certyfikatów pozostałych stron.
3. SSL → Własny → wkleić leaf, odpowiadający key i chain-only. Nie używać globalnej listy certyfikatów do zmiany innych witryn. Nie zapisywać zrzutu ekranu z widocznym kluczem; materiał ma trafić wyłącznie do zatwierdzonego pola tego vhosta przez HTTPS panelu.
4. Włączyć dopiero po zgodzie. Zapisać wynik panelu; w przypadku błędu zakończyć bez zmiany DNS, `www`, zabezpieczeń i ustawień innych witryn.
5. Sprawdzić połączenie TLS z SNI `test.pracowniaform.com`, weryfikacją hostname/chain oraz porównać podawany leaf SHA-256 z lokalnym. Przykład OpenSSL 3:

```text
openssl s_client -connect 195.2.223.12:443 -servername test.pracowniaform.com -verify_hostname test.pracowniaform.com -verify_return_error -CAfile <PRIVATE>/trusted-isrg-roots.pem -no-CApath -no-CAstore -showcerts
```

6. Potwierdzić także zwykłe HTTPS przez DNS bez `-k`/bypass i bez błędu przeglądarki; SAN, daty i fingerprint. Pusty webroot może dawać HTTP403 mimo poprawnego TLS. Lokalna inspekcja Norton może zastąpić przedstawiany certyfikat: wtedy wynik origin jest **niepotwierdzony**; wykonać walidowany test z niezależnego, nieinspekowanego klienta, nie wyłączać ochrony i nie akceptować certyfikatu Nortona jako dowodu leaf LH.
7. Sprzątnąć wyłącznie zatwierdzony TXT po zakończeniu wyzwania. Zostawić `test TXT lh.pl`, A, inne wartości TXT i pozostały DNS bez zmian. Wydać raport PASS/FAIL bez prywatnego klucza.

## 4. Odnowienia i testy narzędzia

Pozostaje ręczne DNS-01 + ponowny import świeżego zestawu według [procedury odnowienia](LH_DNS01_PRIVATE_20261114.md). Brak harmonogramu i potwierdzonej automatycznej reinstalacji przez LH.

[Regresje walidatora](../tests/lh-pem-check.py) używają wyłącznie syntetycznych certyfikatów w prywatnym katalogu poza repo, usuwanym po testach. Obejmują poprawny zestaw oraz odmowę: inny klucz, dodatkowy `www` SAN, inny host, fullchain w leaf, leaf/duplikat w chain, zły fullchain, niewłaściwe zaufanie, leaf/intermediate jako anchor, nadmiarowe dane w kluczu i zbyt krótka ważność. Wynik tych testów nie jest wynikiem prawdziwego certyfikatu LE.

Źródła formatu/weryfikacji: [WACS PEM files](https://www.win-acme.com/reference/plugins/store/pemfiles), [OpenSSL verify](https://docs.openssl.org/3.5/man1/openssl-verify/).
