#!/usr/bin/env python
# -*- coding: utf-8 -*-

class SyntaxNode(object):
    """docstring for SyntaxNode"""
    def __init__(self, source):
        super(SyntaxNode, self).__init__()
        self._source = source
        self._attributeIdx = 0
        self._attributeLen = 0
        self._valueIdx = 0
        self._valueLen = 0
        self._modify = False
        self._children = []

    def getAttribute(self):
        return self._source[self._attributeIdx:self._attributeIdx + self._attributeLen]

    def setAttribute(self, pos, l):
        self._attributeIdx = pos
        self._attributeLen = l

    def getValue(self):
        return self._source[self._valueIdx:self._valueIdx + self._valueLen]

    def setValue(self, pos, l):
        self._valueIdx = pos
        self._valueLen = l

    @property
    def modify(self):
        return self._modify

    @modify.setter
    def modify(self, v):
        self._modify = v

    def childrenCount(self):
        return len(self._children)

    def addChild(self, v):
        self._children.append(v)

    def getChild(self, i):
        if i >= len(self._children):
            return
        return self._children[i]


class Parser(object):
    """docstring for GradleParser"""
    def __init__(self, path):
        super(Parser, self).__init__()
        self.BLANK_CHART = [' ', '\t', '\n', '\r']
        self.BRACKET_CHART = ['{', '}', '[', ']', '(', ')']
        self.filePath = path
        self.contentLength = 0
        self.curPos = 0

    def parser(self):
        self.readFile(self.filePath)

    def readFile(self, path):
        with open(path, 'rb') as f:
            self.content = f.read()
        self.contentLength = len(self.content)

    def readWord(self):
        self.skipBlank()
        begin = self.curPos
        while self.curPos < self.contentLength:
            if self.content[self.curPos] in self.BLANK_CHART or self.content[self.curPos] in self.BRACKET_CHART:
                break
            else:
                self.curPos += 1

        return begin, self.curPos - begin

    def readBracketContent(self):
        self.skipBlank()
        begin = self.curPos
        count = 0
        if self.testChart('{') or self.testChart('('):
            bracketl = self.content[self.curPos]
            if '{' == bracketl:
                bracketr = '}'
            self.curPos += 1
            count += 1
        else:
            print('readBracketContent first chart is invalid')
            return
        while self.curPos < self.contentLength:
            if self.testChart(bracketl):
                count += 1
            elif self.testChart(bracketr):
                count -= 1
            self.curPos += 1

            if 0 == count:
                break

        return begin, self.curPos - begin

    def readString(self):
        self.skipBlank()
        begin = self.curPos
        count = 0
        if self.testChart('\'') or self.testChart('"'):
            bracket = self.content[self.curPos]
            self.curPos += 1
            count += 1
        else:
            print('readString first chart is invalid')
            return
        while self.curPos < self.contentLength:
            if self.testChart(bracket):
                self.curPos += 1
                break
            self.curPos += 1

        return begin, self.curPos - begin

    def readLine(self):
        self.skipBlank()
        begin = self.curPos
        lastChart = self.content[self.curPos]
        while self.curPos < self.contentLength:
            if self.testChart(['\r', '\n']):
                self.curPos += 1
                if lastChart in [':', ',']:
                    continue
                else:
                    break
            else:
                lastChart = self.content[self.curPos]
                self.curPos += 1

        return begin, self.curPos - begin

    def skipBlank(self):
        lineComment = False
        multiComment = False
        while self.curPos < self.contentLength:
            if lineComment:
                if self.testChart(['\r', '\n']):
                    lineComment = False
                self.curPos += 1
                continue

            if multiComment:
                if '*/' == self.content[self.curPos: self.curPos  + 2]:
                    multiComment = False
                    self.curPos += 2
                else:
                    self.curPos += 1
                continue

            if self.content[self.curPos] in self.BLANK_CHART:
                self.curPos += 1
            elif '//' == self.content[self.curPos: self.curPos + 2]:
                self.curPos += 2
                lineComment = True
            elif '/*' == self.content[self.curPos: self.curPos + 2]:
                self.curPos += 2
                multiComment = True
            else:
                break

    def testChart(self, charts, pos = None):
        if not pos:
            pos = self.curPos
        if not isinstance(charts, list):
            charts = [charts]
        if self.content[pos] in charts:
            return True
        else:
            return False

    def increase(self, step = 1):
        self.curPos += step
        self.skipBlank()

    def reachEOF(self):
        if self.curPos < self.contentLength:
            return False
        return True

    def save(self):
        pass


class GradleParser(Parser):
    """docstring for GradleParser"""
    def __init__(self, arg):
        super(GradleParser, self).__init__(arg)

    def parser(self):
        super(GradleParser, self).parser()

        root = SyntaxNode(self.content)
        self.root = root
        root.setAttribute(0, self.contentLength)
        root.setValue(0, self.contentLength)
        self.parserSyntaxNode(root)

        self.dump()

    def parserSyntaxNode(self, parent):
        resavedPos = self.curPos
        resavedLen = self.contentLength
        self.curPos = parent._valueIdx
        self.contentLength = parent._valueIdx + parent._valueLen

        while True:
            self.skipBlank()
            if self.reachEOF():
                break
            if '{' == self.content[self.curPos]:
                self.increase()

            b, l = self.readWord()
            if not l:
                break
            syntaxNode = SyntaxNode(self.content)
            syntaxNode.setAttribute(b, l)
            b, l = self.readArgs()
            syntaxNode.setValue(b, l)

            parent.addChild(syntaxNode)

            attribute = syntaxNode.getAttribute()
            if 'dependencies' == attribute or 'android' == attribute or 'defaultConfig' == attribute:
                self.parserSyntaxNode(syntaxNode)

        self.curPos = resavedPos
        self.contentLength = resavedLen

    def readArgs(self):
        self.skipBlank()
        if self.testChart('{') or self.testChart('('):
            return self.readBracketContent()
        elif self.testChart('\'') or self.testChart('"'):
            return self.readString()
        else:
            return self.readLine()

    def addDependency(self, key, lib):
        pass

    def dump(self):
        root = self.root
        print('>>>>>>>>>>>>>B')
        print('Root: child count:{0}'.format(root.childrenCount()))
        for i in xrange(0, root.childrenCount()):
            print('Node {0}'.format(i))
            self.dumpNode(root.getChild(i))
        print('>>>>>>>>>>>>>E')

    def dumpNode(self, syntaxNode):
        print('Arrtitue: {0}'.format(syntaxNode.getAttribute()))
        print('Args: {0}'.format(syntaxNode.getValue()))

        for i in xrange(0, syntaxNode.childrenCount()):
            print('Node {0}'.format(i))
            self.dumpNode(syntaxNode.getChild(i))

def main():
    parser = GradleParser('./build.gradle')
    parser.parser()
    parser.addDependency('compile', 'com.sdkbox.groud:test:1.2.0')
    parser.save()


if __name__ == '__main__':
    main()
