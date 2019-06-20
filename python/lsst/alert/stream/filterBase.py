# This file is part of alert_stream.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
