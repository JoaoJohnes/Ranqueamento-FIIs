# Ranqueamento-FIIs
Projeto desenvolvido para o TCC do curso de Ciência da Computação

O executavel main.exe está localizado dentro da pasta dist, após execução é gerado um arquivo chamado output.xlsx, contendo uma planilha com os resultados.

Necessário ter o navegador firefox instalado para o webdriver executar corretamente.

------ Branch com base de dados --------------
a branch database-version contém a versão com base de dados, ela não contém executavel
para execução necessário: 
- instalação MariaDB, e conector MariaDB-Python-C (https://mariadb.com/docs/server/connect/programming-languages/c/)
- linha 25 main.py alterar a string de conexão da engine, colocando dados do MariaDB  / engine = sqlalchemy.create_engine("mariadb+mariadbconnector://**usuário**:**senha**@**servidor-ip**:**port**/fiis") /
- criar a base de dados, sql com criação da base tabelas e inserções, contino arquivo fiis.sql
- ter python instalado, versão utilizada no desenvolvimento = 3.12
- firefox instalado
- para execução: Python3.12 ./main.py , alterar versão do python caso necessário.
