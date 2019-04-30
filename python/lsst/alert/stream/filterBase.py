
__all__ = ['AlertFilter', 'Exporter', 'StreamExporter']


class AlertFilter(object):

    def __init__(self, outputStream):
        self.outputStream = outputStream
        self.visitId = 'visitId'

    def __call__(self, schema, alert):
        visit = self.getVisit(alert)
        if visit != self.visitId:
            self.alertCount = 1
            self.visitId = visit
        if self.filter(alert) and self.alertCount <= 20:
            self.alertCount += 1
            self.outputStream(schema, alert)

    def getVisit(self, alert):
        ccdVisitId = alert['diaSource']['ccdVisitId']
        # TODO Visit ID scraping will depend on format of ccdVisitId
        visit = str(ccdVisitId)[-5:]
        return visit

    def filter(self, alert):
        raise NotImplementedError


class Exporter(object):

    def __call__(self, schema, alert):
        self.export(schema, alert)

    def export(self, schema, alert):
        raise NotImplementedError


class StreamExporter(Exporter):

    def __init__(self, producer):
        self.producer = producer

    def export(self, schema, alert):
        self.producer.send(schema, alert)
