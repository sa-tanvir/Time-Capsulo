# Functional specification

## 1. Component overview

`LinkedTreeMap.rebalance(unbalanced, insert)` restores the AVL balance of the map's binary search tree after a node was added below, or removed from below, the node `unbalanced`. It walks from `unbalanced` up to the root of the tree, correcting the stored heights and performing the AVL rotations needed so that for every node on that path the heights of its two subtrees differ by at most 1.

## 2. Functional requirements

For `node = unbalanced`, then `node.parent`, then its parent, and so on up to the tree root (stop at `null`), do the following. Let `leftHeight` / `rightHeight` be the heights of `node.left` / `node.right` (0 for a missing child), and `delta = leftHeight - rightHeight`.

- `delta == 0` or `delta == 1` or `delta == -1`: the node is balanced; set `node.height = max(leftHeight, rightHeight) + 1`.
- `delta == -2` (right-heavy): let `rightDelta = height(right.left) - height(right.right)` (missing children count 0).
  - If `rightDelta == -1`, or `rightDelta == 0` **and** `insert` is `false` (removal): rotate left at `node` (single rotation).
  - Otherwise (`rightDelta == 1`; with `insert` true a delta of 0 cannot occur): rotate right at `node.right`, then rotate left at `node` (double rotation).
- `delta == 2` (left-heavy): symmetric. Let `leftDelta = height(left.left) - height(left.right)`. If `leftDelta == 1`, or `leftDelta == 0` and `insert` is `false`: rotate right at `node`. Otherwise (`leftDelta == -1`): rotate left at `node.left`, then rotate right at `node`.
- The rotations (`rotateLeft`, `rotateRight`) fix parent links, the heights of the nodes they move, and, when the rotated node was the root of its tree, the tree's root reference (`root`).
- After a rotation (single or double), the walk continues with the new root of the rotated subtree (its height is already correct after the rotation) and then with that node's parent, and so on up to the tree root.
- Equivalent early exits are permitted but not required: when inserting, nothing above the first node whose height is unchanged or the first rotation needs any change; when removing, nothing above the first node whose height is unchanged needs any change.

After the call the whole tree must be a valid AVL tree with correct stored heights, and the shape must be exactly the one given by the rules above (the choice between single and double rotation, and the tie-break on removal, are observable through the tree shape).

## 3. Input specification

- `unbalanced`: the lowest node whose subtree height may have changed: for an insertion the parent of the newly attached node; for a removal the parent of the node that was removed (its former parent). May be `null` (nothing to do) when a root was removed.
- `insert`: `true` if the call follows an insertion, `false` if it follows a removal.
- Precondition: apart from the nodes on the path from `unbalanced` to the root, the tree is a valid AVL tree with correct heights, and every node on that path has a balance difference of at most 2 in magnitude.

## 4. Output specification

No return value; the tree is modified in place (links, heights, root reference, `root`). Example (insertion of keys 1, 2, 3 in this order into an empty map): after inserting 3 the node 1 has `delta == -2`, its right child 2 has `rightDelta == -1`, so a left rotation makes 2 the root with children 1 and 3, heights 2, 1, 1.

## 5. Edge cases and constraints

- `unbalanced == null` is a no-op.
- No exception is thrown for a valid tree.
- Runs in time proportional to the height of the tree.
