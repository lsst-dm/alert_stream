
__all__ = ['AlertFilter', 'Exporter', 'StreamExporter']


class AlertFilter(object):

    def __init__(self, topic):
        self.topic = topic

    def __call__(self, alert):
        self.visit = self.getVisit(alert)
        if self.filter(alert):
            return True
        else:
            return False

    @staticmethod
    def getVisit(alert):
        ccdVisitId = alert['diaSource']['ccdVisitId']
        # TODO Visit ID scraping will depend on format of ccdVisitId
        visit = str(ccdVisitId)[-5:]
        return visit

    def filter(self, alert):
        raise NotImplementedError


class Exporter(object):

    def __init__(self):
        self

    def __call__(self, alert):
        self.export(alert)

    def export(self, alert):
        raise NotImplementedError


class StreamExporter(Exporter):

    def __init__(self, producer):
        self.producer = producer
        self.schema = producer.alert_schema
        self.topic = producer.topic

    def export(self, alert):
        self.producer.send(alert, encode=True)
