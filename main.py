from datetime import datetime

import requests
from lxml import html

disciplines = {5: 'Программирование игр на Python',
               4: 'Программирование на JavaScript',
               29: 'Создание чат-ботов на Python для ВК и Telegram',
               75: 'Minecraft - программирование на Python',
               49: 'Python и JavaScript - игровое программирование в CodeCombat',
               36: 'Презентация PowerPoint',
               54: 'Программирование Minecraft',
               51: 'Программирование для самых маленьких в  Tynker',
               85: 'Создание игр в Roblox Studio',
               119: 'Программирование на Python',
               106: 'Minecraft - введение в искусственный интеллект',
               130: 'Minecraft - программирование на JavaScript',
               138: 'Программирование на Python3',
               128: 'Разработка модов для Minecraft'}


def get_verify_code_by_team_ID(session, team_id):
    token = session.cookies.get('.ASPXAUTH')
    headers = {'Cookie': f'.ASPXAUTH={token}'}
    hw_view = session.request('GET', f'https://coddy.t8s.ru/Lesson/EditPlan?learnerId={team_id}', headers=headers)
    tree = html.fromstring(hw_view.text)
    verifyCode = tree.xpath('//input[@id="VerifyCode"]')[0].get('value')
    return verifyCode


def get_team_url():
    team_url = input('\nВВЕДИ ССЫЛКУ НА МОДУЛЬ ГРУППЫ ИЛИ ИНДИВА: ')
    while 'group' not in team_url.lower() and 'individual' not in team_url.lower():
        print('ERROR: некорректная ссылка')
        team_url = input('\nВВЕДИ ССЫЛКУ НА МОДУЛЬ ГРУППЫ ИЛИ ИНДИВА (https://coddy.t8s.ru/Learner/Group/00000): ')
    return team_url


def get_team_ID(team_url):
    teamID = team_url.split('/')[-1]
    if not teamID.isdigit():
        print('\nНе найден ID группы')
        return
    print('\nНайден ID группы:', teamID)
    return teamID


def get_group_view(session, team_url):
    group_view = session.get(team_url)
    if not group_view.ok:
        print('Не удалось открыть страницу группы')
        return
    return group_view


def get_payer_ID(treeHTML):
    payerID = treeHTML.xpath('//div[@data-card-scheme]')[0].get('data-card-scheme').split('p')[-1]
    return payerID


def get_module_dates(session, team_id, payer_id=None):
    token = session.cookies.get('.ASPXAUTH')
    headers = {'Cookie': f'.ASPXAUTH={token}'}
    if payer_id:
        data = session.request('GET', f'https://coddy.t8s.ru/DayScheme/GetPayerScheme/{team_id}?payerId={payer_id}',
                               headers=headers).json()
    else:
        data = session.request('GET', f'https://coddy.t8s.ru/DayScheme/GetLearnerScheme/{team_id}',
                               headers=headers).json()
    dates = []
    for x in data['Scheme']:
        if x['JsType'] not in [4, 5, 6]:
            dates.append(x['DateString'])
    if not dates:
        print('\nДаты не распознаны')
        return
    return dates


def get_complete_personal_dates(session, teacherID, studentID):
    token = session.cookies.get('.ASPXAUTH')
    headers = {'Cookie': f'.ASPXAUTH={token}'}
    personal_scores = session.request('GET', f'https://coddy.t8s.ru/Test/StudentTests/{studentID}', headers=headers)
    treeHTML = html.fromstring(personal_scores.text)
    complete_dates = []
    for x in map(str,
                 treeHTML.xpath(f'//tbody//a[@href="/Profile/{teacherID}"]/../../td/x-small-font-block/../text()')):
        if (d := x.strip('\r\n 0"').rsplit('.', 1)[0]):
            complete_dates.append(d)
    return complete_dates


def get_complete_HW_dates(treeHTML):
    months = {'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
              'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12}
    complete_dates = []
    for x in map(str, treeHTML.xpath('//table[@data-ajaxforms-token="ListTable"]//tr/td[2]/text()')):
        x = x.split()
        complete_dates.append(f'{x[0]}.{str(months[x[1]]).zfill(2)}')
    return complete_dates


def find_lost_dates(complete_dates, module_dates):
    lost_dates = module_dates[:]
    for x in complete_dates:
        if x in lost_dates:
            lost_dates.remove(x)
    if lost_dates:
        print('даты занятий:', *lost_dates)
        return lost_dates
    return None


def get_teacher_ID(treeHTML):
    teacherID = treeHTML.xpath('//a[@href and text()="Профиль"]')[0].get('href').split('/')[-1]
    if len(teacherID) <= 0:
        print('\nНе найден препод')
        return
    print('\nНайден препод:', teacherID)
    return teacherID


def get_discipline_name(treeHTML):
    disciplineName = treeHTML.xpath('//td[.="Дисциплина:"]/../td[2]')[0].text_content()
    if len(disciplineName) <= 0:
        print('\nНе найдено имя дисциплины')
        return
    print('\nДисциплина:', disciplineName)
    return disciplineName


def get_discipline_ID(dictionary, name):
    for disciplineID, v in dictionary.items():
        if v == name:
            return disciplineID
    else:
        print('Не нашли ID дисциплины')
        return


def get_lesson_dates():
    dates = input('\nCкопируйте и вставьте даты занятий в строчку через пробел(23.06 3.11...): ').split()
    if not dates:
        print('\nДаты не распознаны')
        return
    print('\nДаты занятий:', *dates)
    return dates


def get_team_type(team_url):
    if 'group' in team_url.lower():
        return 'group'
    if 'individual' in team_url.lower():
        return 'individual'
    print('Тип группы не распознан')


def find_students(team_type, tree):
    if team_type == 'group':
        studentsTags = tree.xpath('//div[@class="tab-content"]//span[@data-tab-debt]')
        if not studentsTags:
            return
        listStudentsID = [span.get('data-tab-debt') for span in studentsTags]
    elif team_type == 'individual':
        listStudentsID = [tree.xpath('//header[@class="row"]/x-caption/a')[0].get('href').split('/')[-1]]
    else:
        print('Ученики не найдены')
        return
    print('\nНайдены ученики:')
    print('\n'.join(listStudentsID))
    return listStudentsID


def set_homeworks(session, team_id, verify_code, lesson_date):
    lesson_date = lesson_date.split('.')
    date = f'2024-{lesson_date[1]}-{lesson_date[0]}T00:00:00'
    url = 'https://coddy.t8s.ru/Lesson/EditPlan'
    token = session.cookies.get('.ASPXAUTH')
    headers = {'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
               'X-AjaxForms-Tokens': 'LearnerLessonPlans', 'sec-ch-ua-mobile': '?0',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
               'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Accept': 'text/html, */*; q=0.01',
               'X-Requested-With': 'XMLHttpRequest', 'sec-ch-ua-platform': '"Windows"', 'Sec-Fetch-Site': 'same-origin',
               'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty', 'host': 'coddy.t8s.ru',
               'Cookie': f'.ASPXAUTH={token}'}
    data = {'Id': '0', 'VerifyCode': f'{verify_code}', 'LearnerId': f'{team_id}', 'SingleLearnerId': f'{team_id}',
            'Date': date, 'VisibleForClients': 'true', 'Description': '<p>ДЗ в Дискорде</p>',
            'backUrl': f'/Learner/Individual/{team_id}'}
    body = session.post(url, headers=headers, data=data)


def give_fives(session, teacher_id, student_id, discipline_id, lesson_date):
    lesson_date = lesson_date.split('.')
    date_nwds = f'2024-{lesson_date[1]}-{lesson_date[0]}T00:00:00'
    date_time_now = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    url = 'https://coddy.t8s.ru/Test/EditTestResult'
    token = session.cookies.get('.ASPXAUTH')
    headers = {'Accept': 'text/html, */*; q=0.01', 'Accept-Encoding': 'gzip, deflate, br, zstd',
               'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
               'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Cookie': f'.ASPXAUTH={token}',
               'Origin': 'https://coddy.t8s.ru', 'Referer': f'https://coddy.t8s.ru/Profile/{student_id}',
               'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
               'Sec-Ch-Ua-Mobile': '?0', 'Sec-Ch-Ua-Platform': '"Windows"', 'Sec-Fetch-Dest': 'empty',
               'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
               'X-Ajaxforms-Tokens': 'StudentTestsBody', 'X-Requested-With': 'XMLHttpRequest'
               }

    data = {'Id': '0',
            'SkillsJson': '[{"SkillId":"1","SkillName":"Оценка за поведение на уроке","Score":5,"MaxScore":"5","ValidScore":"5"},{"SkillId":"4","SkillName":"Оценка успеваемости на уроке","Score":5,"MaxScore":"5","ValidScore":"5"},{"SkillId":"5","SkillName":"Оценка за выполнение домашнего задания","Score":5,"MaxScore":"5","ValidScore":"5"}]',
            'StudentId': student_id, 'TimeNwds': '20:31', 'DateNwds': date_nwds, 'DateTime': date_time_now,
            'DisciplineId': discipline_id, 'TeacherId': teacher_id, 'TestCategoryId': '3', 'TestTypeId': '3',
            'Description': '', 'backUrl': f'/Profile/{student_id}'}
    body = session.post(url, headers=headers, data=data)


def login_and_create_session(session, login: str, password: str):
    payload = {'Id': '0', 'LogLogin': f'{login}', 'LogPassword': f'{password}', 'LogRememberMe': 'false'}
    headers = {'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
               'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'Upgrade-Insecure-Requests': '1',
               'Content-Type': 'application/x-www-form-urlencoded',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
               'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-User': '?1',
               'Sec-Fetch-Dest': 'document', 'host': 'coddy.t8s.ru'}
    response = session.post(url, headers=headers, data=payload, allow_redirects=True)
    if response.ok:
        for redirect in response.history:
            cookies = redirect.cookies
            if '.ASPXAUTH' in cookies:
                print('\nБУ-ГА-ГА-ШЕНЬКА\nмы залезли')
                return session
        else:
            print('\nОшибка авторизации')
            print('Логин/пароль введен неверно')
    else:
        print('Не удалось выполнить вход coddy.t8s.ru')


url = 'https://coddy.t8s.ru/'
session = requests.Session()
while not session.cookies:
    LOGIN = input("Введите логин:")
    PASSWORD = input("Введите пароль:")
    session = login_and_create_session(session, LOGIN, PASSWORD)


def main():
    run = True
    while run:
        team_url = get_team_url()
        group_view = get_group_view(session, team_url)
        treeHTML = html.fromstring(group_view.text)
        teamType = get_team_type(team_url)
        payerID = get_payer_ID(treeHTML)
        teamID = get_team_ID(team_url)
        verifyCode = get_verify_code_by_team_ID(session, teamID)
        list_students_id = find_students(teamType, treeHTML)
        teacherID = get_teacher_ID(treeHTML)
        disciplineName = get_discipline_name(treeHTML)
        disciplineID = get_discipline_ID(disciplines, disciplineName)
        moduleDates = None
        if teamType == 'group':
            moduleDates = get_module_dates(session, teamID)
        elif teamType == 'individual':
            moduleDates = get_module_dates(session, teamID, payerID)
        print('\n\n         Проставление домашек')
        dates = find_lost_dates(get_complete_HW_dates(treeHTML), moduleDates)
        if None not in (teamID, verifyCode, dates):
            if input('\n\nПроставить домашки?(да/нет): ').lower().strip() in ['да', 'lf', 'y', 'yes']:
                print()
                for date in dates:
                    print(f'Проставим домашку группе {teamID} за {date}')
                print()
                if input('Все верно? Заношу ДЗ в CRM?(да/нет): ').lower().strip() in ['да', 'lf', 'y', 'yes']:
                    for date in dates:
                        set_homeworks(session, teamID, verifyCode, date)
                        print('*тык*')
                    print()
        elif not dates:
            print('--->Не требуется проставление домашек')
        elif not verifyCode:
            print('--->Отсутствует код верификации для домашек')
        elif not teamID:
            print('--->Ошибка ИД группы')
        print('\n\n         Проставление оценок')
        if None not in (teacherID, disciplineName):
            if input('Проставить оценки?(да/нет): ').lower().strip() in ['да', 'lf', 'y', 'yes']:
                print()
                for studentID in list_students_id:
                    dates = find_lost_dates(get_complete_personal_dates(session, teacherID, studentID), moduleDates)
                    if dates:
                        for date in dates:
                            print(f'Проставим оценку {studentID} за {date}')
                    else:
                        print(f'--->Не требуется проставление оценок для {studentID}')
                if input('\nВсе верно? Заношу оценки в CRM?(да/нет): ').lower().strip() in ['да', 'lf', 'y', 'yes']:
                    print()
                    for studentID in list_students_id:
                        dates = find_lost_dates(get_complete_personal_dates(session, teacherID, studentID), moduleDates)
                        if dates:
                            for date in dates:
                                give_fives(session, teacherID, studentID, disciplineID, date)
                                print('*тык*')
                        else:
                            print(f'--->Не требуется проставление оценок для {studentID}')
        elif not disciplineName:
            print('--->Имя дисциплины не найдено')
        elif not teacherID:
            print('--->Ошибка ИД тичера')
        run = True if input('\n\nПОВТОРИТЬ для другой группы?(да/нет): ').lower() in ['да', 'lf', 'y', 'yes'] else False


if __name__ == '__main__':
    main()
