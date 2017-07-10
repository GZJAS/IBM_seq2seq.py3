import torch.nn as nn
from .baseRNN import BaseRNN

from IPython.core.debugger import Tracer 
debug_here = Tracer() 

class EncoderRNN(BaseRNN):
    r"""
    Applies a multi-layer RNN to an input sequence.
    Args:
        vocab (Vocabulary): an object of Vocabulary class
        max_len (int): a maximum allowed length for the sequence to be processed
        hidden_size (int): the number of features in the hidden state `h`
        input_dropout_p (float, optional): dropout probability for the input sequence (default: 0)
        dropout_p (float, optional): dropout probability for the output sequence (default: 0)
        n_layers (int, optional): number of recurrent layers (default: 1)
        rnn_cell (str, optional): type of RNN cell (default: gru)

    Inputs: inputs, volatile
        - **inputs**: list of sequences, whose length is the batch size and within which each sequence is a list of token IDs.
        - **volatile** (bool, optional): boolean flag specifying whether to preserve gradients, when you are sure you
          will not be even calling .backward().
    Outputs: output, hidden
        - **output** (batch, seq_len, hidden_size): tensor containing the encoded features of the input sequence
        - **hidden** (num_layers * num_directions, batch, hidden_size): tensor containing the features in the hidden state `h`

    Examples::

         >>> encoder = EncoderRNN(input_vocab, max_seq_length, hidden_size)
         >>> output, hidden = encoder(input)

    """
    def __init__(self, vocab, max_len, hidden_size,
            input_dropout_p=0, dropout_p=0,
            n_layers=1, rnn_cell='gru'):
        super(EncoderRNN, self).__init__(vocab, max_len, hidden_size,
                input_dropout_p, dropout_p, n_layers, rnn_cell)

        self.embedding = nn.Embedding(self.vocab.get_vocab_size(), hidden_size)
        self.lengths = None

    def forward(self, *args, **kwargs):
        batch = args[0]
        self.lengths = [min(self.max_len, len(seq)) for seq in batch]
        return super(EncoderRNN, self).forward(batch, **kwargs)

    def forward_rnn(self, input_var):
        """
        Applies a multi-layer RNN to an input sequence.

        Args:
            input_var (batch, seq_len): tensor containing the features of the input sequence.

       returns: output, hidden
            - **output** (batch, seq_len, hidden_size): variable containing the encoded features of the input sequence
            - **hidden** (num_layers * num_directions, batch, hidden_size): variable containing the features in the hidden state h
        """
        embedded = self.embedding(input_var)
        embedded = self.input_dropout(embedded)
        embedded = nn.utils.rnn.pack_padded_sequence(embedded, self.lengths, batch_first=True)
     
        output, hidden = self.rnn(embedded)
        output, _ = nn.utils.rnn.pad_packed_sequence(output, batch_first=True)
        return output, hidden
