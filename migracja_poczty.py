import imaplib
import json
import sys
from datetime import datetime

year = str(sys.argv[1]) # parametr do uruchamiania z konsoli
with open("konta.json", "r") as f: # odczyt z pliku json
    konta = json.load(f)
acc_count = len(konta)
current_acc = 1


def zmiana_typu_zapis_do_tab(boxes):  #eliminacja znaków z nazw skrzynek i zapis do tabeli
    tablica = []
    for i in boxes:
        c = str(i)
        b = c.split('"/"')[1].strip()
        # if b[0] == '"':  Nie mozna usuwac tych cudzysłowiów one pozwalaja na uzycie nazwy skrzynki ze spacja przy najmniej na tym etapie jest to nie prawidłowe
        #     b = b[1:]
        if b[-1] == "'":
            b = b[:-1]
        # if b[-1] == '"':
        #     b = b[:-1]
        tablica.append(b)
    return tablica



def eliminacja_znakow(element):  #kolejna elimincja znakow
    tab_skrzy = []
    for ele in element:
        ele = ele.replace('/', ".")
        if '\\\\' in ele:
            ele = ele.replace("\\\\", "\\")
        else:
            ele = ele.replace("\\", "")
        tab_skrzy.append(ele)
    return tab_skrzy


def tworzenie_skrzynki(path):
    mail2.create(path) #tworzenie skrzynki na podstawie struktury
    mail2.subscribe(path) # dodawanie subskrybcji do skrzynki


def wybor_wiad_z_szkrz(skrzynki_zr, skrzynki_doc, year): # wybieranie wiedomosci z konkretnego folderu
    index = 0  # indexacja do folderow
    year = int(year)
    year += 1  # zwiekszenie roku o 1
    before_date = '(SINCE "01-Nov-2019")'  # zakres datowy pobieranych wiadomosci
    box_count = len(skrzynki_zr)
    for skrzynka in skrzynki_zr:
        mes = skrzynki_zr[index]  # przypisanie folderu w skrzynce pod zmienna z okreslonym indexem
        try:
            if '\\\\' in mes:
                mes = mes.replace("\\\\", "\\")
            else:
                mes = mes.replace("\\", "")
            mail.select(mes)  # eliminacja znaku w nazwie jezeli wystepuje
        except:
            file = open("problem_kodowania.txt",
                        "a")  # gdyby powyzsze proby kodowanie i decodowanie i powidoly sie to zostaje taka informacja zapisana do pliku
            file.write(konto['login_from'] + " " + str(mes))
            file.write("-------------------------------------------------------------------------\n")
            file.close()

        typ, mails = mail.search(None, before_date)  # wyselekcjonowanie tylko i wylacznie wiadomosci z takimi parametrami

        a = str(mails[0])  # zmiana typu na string w celu manipulowania na zmiennej ktora zawiera liste wiadomosci zmieniona na string zeby wyciagac je pokolei
        messages_id = a[2:-1].split(" ")  # eliminacja znaków z konca i poczatku  bitowe oznaczenie
        count = 0 # licznik ilosci wiadomosci
        if len(messages_id) > 0 and messages_id[0]: #sprawdzanie czy sa jakies wiadomosci i czy zawieraja wiecej niz 0 znakow
            count = len(messages_id)  # przypisanie dlugosci do zmiennej
        # print(mes + " " + str(count))
        if count:
            if skrzynki_doc[index].startswith('"') and skrzynki_doc[index].endswith('"'):# sprawdzanie znkaow z poczatku i konca
                name = skrzynki_doc[index][1:-1]  # jezeli wystepuja takie znaki to wycina je
            else:
                name = skrzynki_doc[index]  # jezeli nie ma zanakow zostawia nazwe w takiej postaci
            path = '"{}"'.format(name)  # przypisanie sciezki plikow archiwalnych
            tworzenie_skrzynki(path)  # funkcja tworzy foldery na podstawie sciezki
            mail_index = 1  # kolejny folder
            for msg_new in messages_id:  # petla wyciagajaca pokolei wiadomosci

                global t3
                global seen2
                print(str(konto['login_from']) + " " + str(skrzynki_doc[index]) + " " + str(mail_index) + "/" + str(count) + " : " + str(index + 1) + "/" + str(box_count))
                mail_index += 1

                testowa = mail.fetch(msg_new, "(FLAGS INTERNALDATE BODY.PEEK[])")  # sprawdzanie wiadomosci o okreslonych parametrach
                try:
                    t3 = testowa[1][0][1].decode('iso-8859-2').encode('iso-8859-2')  # sprawdzanie czy takie decodowanie i codowanie dziala
                except:
                    try:
                        t3 = testowa[1][0][1].decode('utf-8').encode('utf-8')  # ewentualnie sprawdzanie czy takie decodowanie i kodowanie dziala
                    except:
                        file = open("problem_kodowania.txt", "a")  # gdyby powyzsze proby kodowanie i decodowanie i powidoly sie to zostaje taka informacja zapisana do pliku
                        file.write(konto['login_from'] + " ")
                        file.write(msg_new + " \n")
                        file.write("-------------------------------------------------------------------------\n")
                        file.close()
                    pass
            # if msg_new == '18':
            #     print("")
                # t2 = str(testowa[1][0][1])[2:].encode('utf-8').str
                try:
                    t3

                    seen = testowa[1][0][0]  # sprawdzanie falgi wiadomosci
                    seen2 = str(seen)
                    if '\\Deleted' not in seen2:  # jezeli wystapi flad=ga deleted to wiadomosc nie zostanie przeniesiona
                        if '\\Seen' in seen2:
                            copy_result = mail2.append(path, '\\Seen', None, t3)  # wiadomosci z flaga seen zostaja przeniesione do skrzynin archiwalnej
                        else:
                            copy_result = mail2.append(path, None, None, t3)  # pozostale wisdomosci rowniez sa przenoszone oczywiscie poza deleted
                except:
                    pass
        index += 1  # kolejny podfolder


for konto in konta:  #iterowanie po dostępach z pliku json
    print(str(konto['login_from']) + ' ' + str(current_acc) + '/' + str(acc_count))
    current_acc += 1
    try:
        mail = imaplib.IMAP4_SSL("imap")
        mail.login(konto['login_from'], konto['pass_from'])
        mail2 = imaplib.IMAP4_SSL("imap")
        mail2.login(konto['login_to'], konto['pass_to'])
        resp, data = mail.list('""', '"*"')  #pobranie informacji o wszystkich podfolderow ze skrzynki zrodlowej
        skrzynki = zmiana_typu_zapis_do_tab(data)
        skrzynki_docelowe = eliminacja_znakow(skrzynki)
        # tworzenie_skrzynki(skrzynki_docelowe)
        wybor_wiad_z_szkrz(skrzynki, skrzynki_docelowe, year)
        mail.logout()
        mail2.logout()
    except Exception as e:
        czas = datetime.now()
        file = open("problem_kodowania_{}.txt".format(czas.strftime('%Y%m%d%H%M%S')), "a")  # gdyby powyzsze proby polaczenia sie z wybrana skrzynka mailowa nie powiedzie się zostaje ten fakt zapisany do pliku
        file.write(czas.strftime('%Y-%m-%d %H:%M:%S') + " " + konto['login_from'] + " ")
        file.write(str(e) + " \n")
        file.write("-------------------------------------------------------------------------\n")
        file.close()
        print(e)
        pass

