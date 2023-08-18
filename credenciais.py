import locale
from datetime import datetime

locale.setlocale(locale.LC_TIME, 'pt_BR')
hoje = datetime.now()
mes = datetime.strftime(hoje, '%B').upper()
ano = datetime.strftime(hoje, '%Y')
n_oficio = '000'

API_KEY_MAPS = 'AIzaSyB1U1Ol3XO2rJ9g1teUU1lfteEy6_5GVSE'

segredos = dict(NOME_USUARIO='007msn88', SENHA='warcraft2718')
segredosCABV = dict(NOME_USUARIO='67144039253', SENHA='050402')
lancamentosCABV = dict(PRESENTE=f'Compareceu nesta CABV para assinatura digital referente ao mês de {mes}/{ano}.',
                       AUSENTE=f'NÃO COMPARECEU nesta CABV para assinatura digital referente ao mês de {mes}/{ano}.',
                       FORAGIDO=f'O reeducando não retornou após o término da PRISÃO ALBERGUE DOMICILIAR e foi '
                                f'INCLUÍDO na relação de FORAGIDOS, por não ter se apresentado espontaneamente '
                                f'nesta CABV no mês de {mes}/{ano} para assinatura de frequência digital e teve '
                                f'sua conduta classificada como MÁ, em conformidade com o art. 50, V da LEP. Foi '
                                f'transferido o cadastro do reeducando para unidade DICAP através do OFÍCIO Nº '
                                f'{n_oficio}/2023/SEJUC/DESIPE/ALBER/ADM.')
