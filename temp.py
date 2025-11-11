epochs = None
data_loader = None
model = None
loss_function = None
optimizer = None


for epoch in range(epochs):  # one epoch is one full pass through the training data

    model.train()  # ensure model is in training mode

    for batch in data_loader:
        # the data_loader provides batches of training data
        # each batch contains data/samples (spectrograms of audio clips)
        # and labels (0/1 for absence/presence of each class, per audio clip)
        data, labels = batch

        # Forward pass
        outputs = model(data)

        # Compute loss: error between predicted and true labels
        loss = loss_function(outputs, labels)

        # clear gradients from previous backwards passes
        optimizer.zero_grad()

        # Backward pass: compute gradients of the loss with respect to model parameters
        loss.backward()

        # Update model parameters using the computed gradients
        # To reduce the loss, we take a step in the direction of the negative gradient
        # roughly: updated_parameter = parameter - dLoss/dParameter * learning_rate
        optimizer.step()

    # at the end of the epoch, we might evaluate the model on a validation set



