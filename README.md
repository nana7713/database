src下的是持久化代码
models下的类对应了表 dao下的类包含了增删改查的基本操作
根据这个结构补充各自业务线的部分
base.py配置了数据库管理器
因为get_session方法使用了@contextmanager注解 配合with来使用就可以自动完成commit和rollback和关闭session的操作
@contextmanager
    def get_session(self):
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
所以再编写dao时可以省去一些重复的步骤
