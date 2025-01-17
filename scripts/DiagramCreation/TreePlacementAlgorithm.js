class DrawTree {
    constructor () {
        this.nodeSize = 0;
        this.siblingDistance = 1;
        this.treeDistance = 1;
    }

    calculatePositions(rootNode) {
        calculateIndividualPositions(rootNode);
        this.checkOverlappingTrees(rootNode.children);
        //this.makeSquareDiagram(rootNode.children, 3); TODO: Fix this
    }

    calculateIndividualPositions(rootNode) {
        rootNode.children.forEach(child => {
            this.calculateInitialX(child);
            this.checkAllChildrenOnScreen(child);
            this.calculateFinalPositions(child, 0);
        });
    }


    calculateInitialX(node) {
        node.children.forEach(element => {
            this.calculateInitialX(element);
        });
        if (node.isLeaf()) {
            // if there is a previous sibling in this set, set X to prevous sibling + designated distance
            if (!node.isLeftMost())
                node.X = node.getPreviousSibling().X + this.nodeSize + this.siblingDistance;
            else
                // if this is the first node in a set, set X to 0
                node.X = 0;
        }
        // if there is only one child
        else if (node.children.length == 1) {
            // if this is the first node in a set, set it's X value equal to it's child's X value
            if (node.isLeftMost()) {
                node.X = node.children[0].X;
            } else {
                node.X = node.getPreviousSibling().X + this.nodeSize + this.siblingDistance;
                node.Mod = node.X - node.children[0].X;
            } 
        } else {
            var leftChild = node.getLeftMostChild();
            var rightChild = node.getRightMostChild();
            var mid = (leftChild.X + rightChild.X) / 2;

            if (node.isLeftMost()) {
                node.X = mid;
            } else {
                node.X = node.getPreviousSibling().X + this.nodeSize + this.siblingDistance;
                node.Mod = node.X - mid;
            }
        }
        
        if (node.children.length > 0 && !node.isLeftMost())
        {
            // Since subtrees can overlap, check for conflicts and shift tree right if needed
            this.checkForConflicts(node);
        }

    }

    checkForConflicts(node) {
        var minDistance = this.treeDistance + this.nodeSize;
        var shiftValue = 0;

        var nodeContour = new Map();
        this.getLeftContour(node, 0, nodeContour);

        var sibling = node.getLeftMostSibling();
        while (sibling != null && sibling != node)
        {
            var siblingContour = new Map();
            this.getRightContour(sibling, 0, siblingContour);
            
            var siblingContourKeys = Array.from(siblingContour.keys());
            var nodeContourKeys = Array.from(nodeContour.keys());

            for (var level = node.Y + 1; level <= Math.min(Math.max(...siblingContourKeys), Math.max(...nodeContourKeys)); level++) {
                var distance = nodeContour.get(level) - siblingContour.get(level);
                if (distance + shiftValue < minDistance)
                {
                    shiftValue = minDistance - distance;
                }
            }

            if (shiftValue > 0) {
                node.X += shiftValue;
                node.Mod += shiftValue;
                
                this.centerNodesBetween(node, sibling);

                shiftValue = 0;
            }

            sibling = sibling.getNextSibling();
        }
    }

    centerNodesBetween(leftNode, rightNode) {
        var leftIndex = leftNode.parent.children.indexOf(rightNode);
        var rightIndex = leftNode.parent.children.indexOf(leftNode);
        
        var numNodesBetween = (rightIndex - leftIndex) - 1;

        if (numNodesBetween > 0) {
            var distanceBetweenNodes = (leftNode.X - rightNode.X) / (numNodesBetween + 1);

            var count = 1;
            for (var i = leftIndex + 1; i < rightIndex; i++)
            {
                var middleNode = leftNode.parent.children[i];

                var desiredX = rightNode.X + (distanceBetweenNodes * count);
                var offset = desiredX - middleNode.X;
                middleNode.X += offset;
                middleNode.Mod += offset;

                count++;
            }

            this.checkForConflicts(leftNode);
        }
    }

    getLeftContour(node, modSum, values) {
        if (!values.has(node.Y))
            values.set(node.Y, node.X + modSum);
        else
            values.set(node.Y, Math.min(values.get(node.Y), node.X + modSum));

        modSum += node.Mod;
        node.children.forEach(child => {
            this.getLeftContour(child, modSum, values);
        });
    }

    getRightContour(node, modSum, values) {
        if (!values.has(node.Y)) {
            values.set(node.Y, node.X + modSum);
        } else {
            values.set(node.Y, Math.max(values.get(node.Y), node.X + modSum));
        }
        modSum += node.Mod;
        node.children.forEach(child => {
            this.getRightContour(child, modSum, values);
        });
    }

    checkAllChildrenOnScreen(node) {
        var nodeContour = new Map();
        this.getLeftContour(node, 0, nodeContour);

        var shiftAmount = 0;
        var nodeContourKeys = Array.from(nodeContour.keys());
        nodeContourKeys.forEach(y => {
            if (nodeContour.get(y) + shiftAmount < 0)
                shiftAmount = (nodeContour.get(y) * -1);
        });

        if (shiftAmount > 0)
        {
            node.X += shiftAmount;
            node.Mod += shiftAmount;
        }
    }
    calculateFinalPositions(node, modSum) {
        node.X += modSum;
        modSum += node.Mod;

        node.children.forEach(child => {
            this.calculateFinalPositions(child, modSum);
        });

        if (node.children.length === 0) {
            node.Width = node.X;
            node.Height = node.Y;
        } else {
            node.Width = Math.max(...node.children.map(child => child.Width));
            node.Height = Math.max(...node.children.map(child => child.Height));
        }
    }

    checkOverlappingTrees(nodes) {
        var minDistance = this.treeDistance + this.nodeSize;
        var shiftValue = 0;

        nodes.forEach(node => {
            var index = nodes.indexOf(node);
            if (index != 0) {
                var sibling = nodes[index - 1];
                var nodeContour = new Map();
                var siblingContour = new Map();
                this.getLeftContour(node, 0, nodeContour);
                var maxLeftPoint = Math.max(...this.getAllXValues(node));
                this.getRightContour(sibling, 0, siblingContour);
                var maxRightPoint = Math.max(...this.getAllXValues(sibling));

                var distance = maxLeftPoint - maxRightPoint;
                shiftValue = maxRightPoint+minDistance;

                if (shiftValue > 0) {
                    this.shiftTreeRight(node, shiftValue);
                    var afterShiftContour = new Map();
                    this.getLeftContour(node, 0, afterShiftContour);
                    shiftValue = 0;
                }
            }
        });
    }

    getAllXValues(node) {
        var values = [];
        values.push(node.X);
        node.children.forEach(child => {
            values = values.concat(this.getAllXValues(child));
        });

        return values;
    }

    getMaximumXValueinList(nodes) {
        var values = [];
        nodes.forEach(node => {
            values = values.concat(this.getAllXValues(node));
        });

        return Math.max(...values);
    }
    
    shiftTreeRight(node, shiftValue) {
        node.X += shiftValue;

        node.children.forEach(child => {
            this.shiftTreeRight(child, shiftValue);
        });
    }

    shiftTreeLeft(node, shiftValue) {
        node.X -= shiftValue;

        node.children.forEach(child => {
            this.shiftTreeLeft(child, shiftValue);
        });
    }

    makeSquareDiagram(nodes, treesInFirstRow) {
        var row = -1;
        var column = 0;
        var maxX = 0;
        var firstRow = [];
        var totalX = 0;
        var shiftedTrees = [];
        nodes.forEach(node => {
            if (nodes.indexOf(node) < treesInFirstRow-1) {
                firstRow.push(node);
                if (nodes.indexOf(node) === treesInFirstRow-2) {
                    maxX = this.getMaximumXValueinList(firstRow);
                }
            } else {
                var shiftValue = maxX + this.treeDistance;
                this.shiftTreeLeft(node, shiftValue*(row+1));
                shiftedTrees.push(node);
                totalX += Math.max(this.getAllXValues(node));
                if (totalX > maxX) {
                    var maxY = this.getMaximumYValueinList(shiftedTrees);
                    this.shiftTreeDown(node, maxY + this.treeDistance);
                    shiftedTrees = [];
                }
            }
        });
    }

    getAllYValues(node) {
        var values = [];
        values.push(node.Y);
        node.children.forEach(child => {
            values = values.concat(this.getAllYValues(child));
        });

        return values;
    }

    getMaximumYValueinList(nodes) {
        var values = [];
        nodes.forEach(node => {
            values = values.concat(this.getAllYValues(node));
        });

        return Math.max(...values);
    }

    shiftTreeDown(node, shiftValue) {
        node.Y += shiftValue;

        node.children.forEach(child => {
            this.shiftTreeDown(child, shiftValue);
        });
    }

}