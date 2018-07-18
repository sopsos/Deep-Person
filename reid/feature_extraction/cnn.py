from __future__ import absolute_import
from collections import OrderedDict

from torch.autograd import Variable

from ..utils import to_torch


def extract_cnn_feature(model, inputs, modules=None):
    model.eval()
    inputs = to_torch(inputs)
    inputs = Variable(inputs, volatile=True)
    if modules is None:
        outputs = model(inputs)
        if isinstance(outputs, (tuple, list)):
            outputs = list(outputs)  # do this: because tuple element cannot be modified
            for ix, output in enumerate(outputs):
                outputs[ix] = output.data.cpu()
        else:
            outputs = outputs.data.cpu()
            outputs = [outputs, ]  # make sure outputs is a list
        return outputs
    # Register forward hook for each module
    outputs = OrderedDict()
    handles = []
    for m in modules:
        outputs[id(m)] = None
        def func(m, i, o): outputs[id(m)] = o.data.cpu()
        handles.append(m.register_forward_hook(func))
    model(inputs)
    for h in handles:
        h.remove()
    return list(outputs.values())