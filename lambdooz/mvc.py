from decorator import decorator

@decorator
def mutator(method, self, *args, **kwargs):
    ret = method(self, *args)

    for observer in self._observers:
        observer.update()

    return ret


@decorator
def observer(init, self, model, *args, **kwargs):
    ret = init(self, model, *args, **kwargs)
    model._observers.append(self)
    return ret


@decorator
def observable(init, self, *args, **kwargs):
    ret = init(self, *args, **kwargs)
    self._observers = []
    return ret
