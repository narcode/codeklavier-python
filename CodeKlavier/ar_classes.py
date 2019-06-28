"""
AR extension classes and helper functions
"""

from Mapping import Mapping_CKAR
import random
import asyncio

class CkAR(object):
    """Main class for the AR extension"""
    
    def __init__(self):
        self.trees = 1
        self.mapping = Mapping_CKAR()
        self.navigate = 0
        self._parallelTrees = []
        self.loop = asyncio.get_event_loop()
        self.shapes = []
        self._shapes = {}
        self.shape = 0;
        
        self.receiveState()
        
        
    def run_in_loop(self, json):
        try:
            self.loop.run_until_complete(self.mapping.send(json))
        except:
            print('error sending')
    
    def receiveState(self):
        try:
            state = self.loop.run_until_complete(self.mapping.receive())
            print(state)
        except:
            print('error receiving')
        
        self.trees = state['numTrees']
        for shape in range(0, state['numShapes']):
            self.shapes.append(shape+1)
            
        for tree in range(0, self.trees):
            self._shapes[str(tree+1)] = {}
            self._shapes[str(tree+1)]['shape'] = 1
                
        print('trees and shapes:', self._shapes)
            
    
    def nextT(self):
        """ 
        Traverse the LS trees forward
        """
        self.navigate = self.navigate+1
        if self.navigate == self.trees:
            self.navigate = 0
        nextt = (self.navigate+self.trees)%self.trees
        print('go to next tree', nextt+1)
        self.run_in_loop(self.makeJson('view', str(nextt+1)))

    
    def currentTree(self):
        tree = (self.navigate+self.trees)%self.trees
        return (tree + 1)
        
    def prev(self):
        """ 
        Traverse LS trees backward
        """
        self.navigate = self.navigate-1
        if self.navigate > self.trees:
            self.navigate = 0
        prev = (self.trees + self.navigate)%self.trees
        self.run_in_loop(self.makeJson('view', str(prev+1)))
        print('go to previous tree', prev+1)
    
    
    def toggleShape(self, parallelTrees=False):
        """
        Traverse the possible rendering modes or "shapes" for the AR objects
        """
        
        if not parallelTrees:
            
            tree = self.currentTree()
            self.shape = self._shapes[str(tree)]['shape'] - 1
            
            self.shape += 1
                
            new_shape = self.shapes[self.shape%len(self.shapes)]
            self._shapes[str(tree)]['shape'] = new_shape
            self.run_in_loop(self.makeJsonShape(str(tree), str(new_shape)))

        else:
            if self._parallelTrees == 1:
                self.shape = self._shapes[str(self._parallelTrees[0])]['shape'] - 1
                
            self.shape += 1
            
            new_shape = self.shapes[self.shape%len(self.shapes)]
            for t in self._parallelTrees:
                self._shapes[str(t)]['shape'] = new_shape
                self.run_in_loop(self.makeJsonShape(str(t), str(new_shape)))
                

    def create(self):
        """ 
        Create a new LS tree
        """
        self.trees = self.trees + 1
        self.navigate = self.trees - 1
        self._shapes[str(self.trees)] = {'shape': 1}
        print('create new tree', 'total trees: ', self.trees)
        print('curent trees: ', self._shapes)
        self.run_in_loop(self.makeJson('view', str(self.trees) ))

        
    def select(self, tree=1):
        """ Select a specific LS tree by ID. DEPRECATED
        """
        print('select tree id:', tree)
        
        
    def drop(self, tree=1):
        """ Drop a specific tree from the collection """
        if tree in self._parallelTrees:
            self._parallelTrees.remove(tree)
        else: 
            print('\ntree not created yet or already collected, TREE:', tree, '\n')

        print('drop:', self._parallelTrees)
        
        
    def collect(self, tree=1):
        """Collect a LS-tree for parallel processing"""
        if tree not in self._parallelTrees and tree <= self.trees:
            self._parallelTrees.append(tree)
        else: 
            print('\ntree not created yet or already collected, TREE:', tree, '\n')
            
        print('collected trees:', self._parallelTrees)
        
        
    def storeCollect(self, collection=[]):
        """ store a collection of trees for future calling. Meant to be used inside 
        a function definition
        """
        self._parallelTrees = collection
        print('collection loaded', collection)
        
        
    def transform(self):
        "Send a transorm X Y mesage to the AR engine. X and Y are generated randomly"
        current = self.currentTree()
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        self.run_in_loop(self.makeJsonTransform(str(current), [x, 0, y]))
        print('transform tree', current)
        
    def sendRule(self, string):
        """ send a LS rule via websocket"""
        self.run_in_loop(self.makeJson('lsys', string))        
    
      
    def console(self, string):
        """ send a string to the LS console via websocket"""
        self.run_in_loop(self.makeJson('console', string))        
    
    #TODO: merge these 3 into 1 func:
    def makeJsonTransform(self, tree, position):
        """ make a Json object for spatial Transform"""
        return self.mapping.prepareJsonTransform(tree, position)
    
    
    def makeJsonShape(self, tree, shape):
        """ make a Json object for Shape shift"""   
        return self.mapping.prepareJsonShape(tree, shape)
        
    def makeJson(self, lstype='lsys', payload=''):
        """ make a Json object for L-system rule"""        
        return self.mapping.prepareJson(lstype, payload)
    
    
        

    
    