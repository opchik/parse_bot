import asyncpg
import asyncio
import configparser 

config = configparser.ConfigParser()
config.read("config.ini")

user = config['DATABASE']['user']
password = config['DATABASE']['password']
host = config['DATABASE']['host']
port = config['DATABASE']['port']
database = config['DATABASE']['database']

class BotDB():
    """Класс BotDB используется для взаимодейстия бота и парсера с базой данных.

    Методы, используемые в классе:
    __init__(self)      заполняет данные, необходимые для подключения к БД;
    create_db(self)     создание БД, если она еще не создана;
    create_pool(self)   создание пула обращений к БД;
    release_pool(self)  закрытие пула обращений к БД;
    add_problem(self, all_problems)   добавление задачи в БД;
    get_problem(self, topic=None, difficulty=None)  получение задач из БД и формирование сообщения.

    """
    def __init__(self):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.pool = None


    async def create_db(self):
        create_query = f"""CREATE TABLE IF NOT EXISTS public.parse_data
(
    "number" text,
    name text COLLATE pg_catalog."default",
    topic text[] COLLATE pg_catalog."default",
    complexity bigint,
    solved bigint,
    "url" text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT parse_data_pkey PRIMARY KEY ("url")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.parse_data
    OWNER to postgres;"""

        connection = await asyncpg.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database
        )
        async with connection.transaction():
            await connection.execute(create_query)

    async def create_pool(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database)

    async def release_pool(self):
        await self.pool.close()


    async def add_problem(self, all_problems):
        keys = ', '.join(all_problems[0].keys())
        values = ', '.join([f"({', '.join([str(j) for j in i.values()])})" for i in all_problems])
        query = f'INSERT INTO parse_data ({keys}) VALUES {values};'
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database)
        try:
            connection = await self.pool.acquire()
            await connection.execute(query)
        except Exception as e:
            print(e)

        finally:
            await connection.close()
        

    async def get_problem(self, topic=None, difficulty=None, topic_unique=None):

        if topic_unique!=None and difficulty==None and topic==None:
            query = f"SELECT * FROM parse_data WHERE '{topic_unique}' = ANY (topic) AND array_length(topic, 1) = 1 ORDER BY random() LIMIT 10;"

        elif topic!=None and difficulty==None and topic_unique==None:
            query = f"SELECT * FROM parse_data WHERE '{topic}' = ANY (topic) ORDER BY random() LIMIT 10;"

        elif topic==None and difficulty!=None and topic_unique==None:
            query = f"SELECT * FROM parse_data WHERE complexity = {difficulty} ORDER BY random() LIMIT 10;" 

        elif topic==None and difficulty!=None and topic_unique!=None:
            query = f"SELECT * FROM parse_data WHERE '{topic_unique}' = ANY (topic) AND array_length(topic, 1) = 1"
            query += f" AND complexity = {difficulty} ORDER BY random() LIMIT 10;"


        else:
            return None
        answer = None
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database)

        try:
            connection = await self.pool.acquire()
            answer = await connection.fetch(query)
        
        except Exception as e:
            print(e)

        finally:
            await connection.close()
            if answer==None:
                return None

            res = ''
            for i in answer:
                res += f"Задача: {i[0]}.  ({i[1]})\nТемы: {', '.join(i[2])}\nСложность: {i[3]}\nРешили задачу: x{i[4]}\nhttps://codeforces.com{i[5]}\n\n\n"
            
            return res



