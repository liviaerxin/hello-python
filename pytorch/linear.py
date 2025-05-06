import torch
import torch.nn as nn
import torch.optim as optim

# --- 1. Training Data ---
# y = 2x + 1
X_train = torch.tensor([[1.0], [2.0], [3.0], [4.0]])
y_train = torch.tensor([[3.0], [5.0], [7.0], [9.0]])

# --- 2. Define Model ---
class SimpleLinearModel(nn.Module):
    def __init__(self):
        super(SimpleLinearModel, self).__init__()
        self.linear = nn.Linear(1, 1)

    def forward(self, x):
        return self.linear(x)

model = SimpleLinearModel()

# --- 3. Loss and Optimizer ---
criterion = nn.MSELoss()
optimizer = optim.SGD(model.parameters(), lr=0.01)

# --- 4. Training Loop ---
for epoch in range(200):
    model.train()
    optimizer.zero_grad()
    outputs = model(X_train)
    loss = criterion(outputs, y_train)
    loss.backward()
    optimizer.step()

# --- 5. Print Trained Parameters ---
for name, param in model.named_parameters():
    print(f"{name}: {param.data.numpy()}")

# --- 6. Test Data ---
X_test = torch.tensor([[5.0], [6.0]])
y_test = torch.tensor([[11.0], [13.0]])  # Expected: 2*5+1 = 11, 2*6+1 = 13

# --- 7. Prediction ---
model.eval()
with torch.no_grad():
    predictions = model(X_test)

# --- 8. Evaluation ---
test_loss = criterion(predictions, y_test)
print("\nPredictions:", predictions.numpy())
print("Actual:", y_test.numpy())
print("Test Loss (MSE):", test_loss.item())
