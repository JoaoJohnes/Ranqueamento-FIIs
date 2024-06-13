# Ranqueamento-FIIs
Projeto desenvolvido para o TCC do curso de Ciência da Computação

para execução necessário: 

- instalação MariaDB, e conector MariaDB-Python-C (https://mariadb.com/docs/server/connect/programming-languages/c/)
- linha 25 main.py alterar a string de conexão da engine, colocando dados do MariaDB  / engine = sqlalchemy.create_engine("mariadb+mariadbconnector://**usuário**:**senha**@**ip**:**port**/fiis") /
- criar a base de dados, sql com criação da base tabelas e inserções, contido no arquivo fiis.sql
- ter python instalado, versão utilizada no desenvolvimento = 3.12
- firefox instalado
- para execução: Python3.12 ./main.py , alterar versão do python e path do arquivo caso necessário.
