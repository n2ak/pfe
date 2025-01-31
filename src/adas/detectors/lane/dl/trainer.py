import tqdm
import torch
import typing


class Trainer:

    def __init__(self, model: torch.nn.Module, device="cpu") -> None:
        self.device = torch.device(device)
        self.model = model.to(device=self.device)

        self._compiled = False

    def compile(self, optimizer, loss_fn):
        self.optimizer = optimizer
        self.loss_fn = loss_fn
        self._compiled = True

    def train(self, data_loader, epochs, val_loader=None, log_interval=10):

        if not self._compiled:
            raise Exception("Trainer must be compiled first")
        self.history = {
            "loss": [],
            "accuracy": []
        }
        if val_loader is not None:
            self.history["val_loss"] = []
            self.history["val_accuracy"] = []
        for epoch in range(epochs):
            self.model.train()
            total_loss = 0
            total_correct = 0
            items_treated = 0
            for batch_idx, (data, target) in (bar := tqdm.tqdm(enumerate(data_loader), bar_format="{desc}{bar}")):
                last_batch = (batch_idx == len(data_loader)-1)
                data, target = data.to(self.device), target.to(self.device)
                self.optimizer.zero_grad()
                out = self.model(data)
                loss = self.loss_fn(out, target)
                loss.backward()
                self.optimizer.step()

                total_loss += loss.item()
                pred = out.argmax(dim=1, keepdim=True)
                total_correct += pred.eq(target.view_as(pred)).sum().item()
                items_treated += len(data)
                if (batch_idx % log_interval == 0) or (last_batch):
                    bar.set_description(
                        f'Epoch: {epoch+1} ({100. * (batch_idx+1) / len(data_loader):.0f}%), Loss: {loss.item():.6f}  Acc: {total_correct/items_treated:.2f}'
                    )
                if (last_batch) and (val_loader is not None):
                    val_loss, val_acc = self.validate(
                        val_loader, print_ok=False)
                    loss = total_loss / len(data_loader.dataset)
                    acc = total_correct / len(data_loader.dataset)
                    bar.set_description(
                        f'Epoch: {epoch+1} ({100. * (batch_idx+1) / len(data_loader):.0f}%), Loss: {loss:.6f} Acc: {100. * acc:.2f}'
                        f' val_loss: {val_loss:.6f} val_acc: {val_acc:.6f}'
                    )
            vars = [
                ("loss", loss),
                ("accuracy", acc),
            ]
            if val_loader is not None:
                vars.append(("val_loss", val_loss),)
                vars.append(("val_accuracy", val_acc),)
            self.update_epoch(epoch, self.history, vars)
        return self.history

    def update_epoch(self, epoch: int, hist: dict, vars: typing.List[typing.Tuple[str, float]]):
        for name, item in vars:
            hist[name].append(item)

        # print(f"Epoch {epoch+1}")

    def eval(self, data_loader):
        if not self._compiled:
            raise Exception("Trainer must be compiled first")
        self.model.eval()
        loss = 0
        correct = 0
        with torch.no_grad():
            for (data, target) in data_loader:
                data, target = data.to(self.device), target.to(self.device)
                out = self.model(data)
                loss += self.loss_fn(out, target)
                pred = out.argmax(dim=1, keepdim=True)
                # acc

                correct += pred.eq(target.view_as(pred)).sum().item()
        loss /= len(data_loader.dataset)
        return loss.item(), correct

    def test(self, data_loader):
        loss, correct = self.eval(data_loader)
        print(f'Test set: Average loss: {loss:.4f}, '
              f'Accuracy: {correct}/{len(data_loader.dataset)}'
              f'({100. * correct / len(data_loader.dataset):.0f}%)\n')

    def validate(self, data_loader, print_ok=True):
        loss, correct = self.eval(data_loader)
        acc = correct / len(data_loader.dataset)
        if print_ok:
            print(f'Validation set: Average loss: {loss:.4f}, '
                  f'Accuracy: {correct}/{len(data_loader.dataset)}'
                  f'({100. * acc:.0f}%)\n')
        return loss, acc

    def save_model(self, path: str, save_hist=True):
        torch.save(self.model.state_dict(), path)
        if save_hist:
            hist_path = path.replace(".pt", ".hist.pickle")
            import pickle
            with open(hist_path, "wb") as f:
                pickle.dump(self.history, f)

    @staticmethod
    def load_model(path: str, make_model_fn: typing.Callable[[], torch.nn.Module], print_ok=True, load_hist=True):
        model = make_model_fn()
        model.load_state_dict(torch.load(path))
        history = None
        if load_hist:
            hist_path = path.replace(".pt", ".hist.pickle")
            import os
            if not os.path.exists(hist_path):
                print("History wasn't found")
            else:
                import pickle
                with open(hist_path, "rb") as f:
                    history = pickle.load(f)
        trainer = Trainer(model)
        trainer.history = history

        if print_ok:
            print("Model loaded")
        return trainer

    def plot_hist(self):
        import matplotlib.pyplot as plt
        has_val = "val_loss" in self.history.keys()

        plt.plot(self.history["accuracy"], label="Accuracy")
        if has_val:
            plt.plot(self.history["val_accuracy"], label="Val accuracy")
        plt.ylim([0, 1])
        plt.legend()
        plt.show()

        plt.plot(self.history["loss"], label="Loss")
        if has_val:
            plt.plot(self.history["val_loss"], label="Val loss")
        plt.legend()
        plt.show()
