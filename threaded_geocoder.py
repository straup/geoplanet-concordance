
import datetime
import Queue
import threading

class GeocodeSuccess:
  def __init__(self, line):
    self.status = 'success'
    self.line = line

class GeocodeSkip:
  def __init__(self, line):
    self.status = 'skip'
    self.line = line

class GeocodeFailure:
  def __init__(self, line):
    self.status = 'failure'
    self.line = line

class GeocodeTimeout:
  def __init__(self, line):
    self.status = 'timeout'
    self.line = line

class GeocodeFetch(threading.Thread):
  def __init__(self, queue, outQueue, lineProcessor):
    threading.Thread.__init__(self)
    self.queue = queue
    self.outQueue = outQueue
    self.lineProcessor = lineProcessor

  def run(self):
    while True:
      line = self.queue.get()
      self.processLine(line)
      self.lineProcessor(line)

  def processLine(self, line):
    ret = self.lineProcessor(line)
    if ret == None:
      print 'got no response for %s, no idea why' % line
    else:
      self.outQueue.put(ret)
    self.queue.task_done()

class OutWriter(threading.Thread):
  def __init__(self, queue, outputSuccessFilename, outputFailureFilename):
    self.successOut = open(outputSuccessFilename, 'w')
    self.failedOut = open(outputFailureFilename, 'w')
    threading.Thread.__init__(self)
    self.queue = queue
    self.failCount = 0
    self.totalCount = 0
    self.timeoutCount = 0
    self.skipCount = 0

  def run(self):
    while True:
      g = self.queue.get()
      if g.status == 'skip':
        self.skipCount += 1
        self.failedOut.write((u'SKIP\t' + g.line + u'\n').encode('utf-8'))
      elif g.status == 'timeout':
        self.timeoutCount += 1
        self.failedOut.write((u'TIMEOUT\t' + g.line + u'\n').encode('utf-8'))
      elif g.status == 'failure':
        self.failCount += 1
        self.failedOut.write((u'FAIL\t' + g.line + u'\n').encode('utf-8'))
      elif g.status == 'success':
        self.successOut.write((g.line + u'\n').encode('utf-8'))
      self.totalCount += 1
      if self.totalCount % 1000 == 0:
        print "processed %d lines so far (%d fail, %d 500, %d skip)" % (self.totalCount, self.failCount, self.timeoutCount, self.skipCount)
      self.queue.task_done()

class Reader(threading.Thread):
  def __init__(self, queue, writeQ, inputFile):
    threading.Thread.__init__(self)
    self.queue = queue
    self.writeQ = writeQ
    self.inputFile = inputFile

  def run(self):
    for i, line in enumerate(open(self.inputFile)):
      self.queue.put(line)
    self.queue.join()
    self.writeQ.join()

class ThreadedGeocoder:
  def run(self, inputFile, outputSuccessFile, outputFailureFile, lineProcessor):
    queue = Queue.Queue()
    outQueue = Queue.Queue()

    for i in range(100):
      t = GeocodeFetch(queue, outQueue, lineProcessor)
      t.setDaemon(True)
      t.start()

    w = OutWriter(outQueue, outputSuccessFile, outputFailureFile)
    w.setDaemon(True)
    w.start()

    r = Reader(queue, outQueue, inputFile)
    r.setDaemon(True)
    r.start()

    r.join()
