import struct


class CompileCtx:
    def __init__(self):
        self.output_bytes = b''

        self.labels_override_positions = {} # {byte idx: label name}
        self.label_contents = {} # {label name: position}

    def write_byte(self, b):
        self.output_bytes = self.output_bytes + bytes([b])

    def write_u64(self, b):
        self.output_bytes = self.output_bytes + struct.pack("Q", b)

    def write_labelref(self, label_name):
        self.labels_override_positions[len(self.output_bytes)] = label_name
        self.write_u64(0)

    def write_labelpos(self, label_name):
        self.label_contents[label_name] = len(self.output_bytes)

    def postproc(self):
        resulting_output = self.output_bytes
        for label, position in self.label_contents.items():
            pos_enc = struct.pack("Q", position)

            labels_in_code = [
                idx for idx, clabel in self.labels_override_positions.items()
                if clabel == label
            ]

            for idx in labels_in_code:
                resulting_output = resulting_output[:idx] + pos_enc + resulting_output[idx+len(pos_enc):]

        return resulting_output
