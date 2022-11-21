import scipy.stats as stats

# Default variables
PKT_SIZE = int(1450)
PKT_NUMS = int(2000)
PROP_TIME = int(10)
START_TIME = 0
END_TIME = 5


def transmit(t, size, channel, remained):
    # current available bandwidth (remained bw from prev time + current bw)
    pkt_size = size
    time = t
    bw = remained + channel.bw[time]
    num_packets = 0

    # get the number of packets that can be transmitted at time t and remained bw at time t
    num_packets += int(bw / pkt_size)
    remained_bw = int(bw % pkt_size)

    # if current bw is not sufficient
    while num_packets < 1:
        if time == int(END_TIME * 1000) - 1:  # ms
            break
        time += 1
        bw = remained_bw + channel.bw[time]
        num_packets += int(bw / pkt_size)
        remained_bw = int(bw % pkt_size)

    return time - t + 1, num_packets, remained_bw


class Channel():
    def __init__(self, bandwidth):
        self.bw = bandwidth
        self.prop = PROP_TIME  # ms


class Packet():
    def __init__(self, seq, size):
        # TCP header used in this simulation
        self.src = ""
        self.dst = ""
        self.seq = seq  # sequence number of this packets
        self.ack_seq = 0  # ack sequence

        # used for only simulation, not offical header
        self.start_time = 0  # send start time
        self.ack_arrival = 0  # ack arrival time
        self.bs_arrival = 0  # bs arrival time
        self.recv_arrival = 0  # receiver arrival time

        ################ IMPLEMENT ##################### 
        # define your own observed data here if needed #

        ################################################


class BaseStation():
    def __init__(self, name, threshold):
        self.name = name
        self.queue_length = threshold
        self.queued = []
        self.next_available = 0
        self.remained_bw = 0  # available bw from prev timestep

    def admit(self, t, pkts, downlink):
        loss = [];
        admit = []

        if self.next_available != 0 and self.next_available > t:
            # drop or queue
            for p in pkts:
                if len(self.queued) >= self.queue_length:
                    loss.append(p)
                else:
                    self.queued.append(p)

            return admit, loss

        # downlink admit or not
        if len(self.queued) > 0:
            tx_time, num_packets, remained_bw = transmit(t, PKT_SIZE, downlink, self.remained_bw)
            self.remained_bw = remained_bw
            self.next_available = t + tx_time

            for i in range(0, num_packets):
                p = self.queued.pop(0)
                p.recv_arrival = t + tx_time + PROP_TIME
                admit.append(p)
                # exit if list is empty
                if len(self.queued) == 0:
                    break

        # drop or queue
        for p in pkts:
            if len(self.queued) >= self.queue_length:
                loss.append(p)
            else:
                self.queued.append(p)

        return admit, loss


class Client():
    def __init__(self, src, dst, bandwidth, pkt_list=[], cc=False):
        self.src = src;
        self.dst = dst;
        self.cc = cc

        # variables for senders
        self.pkt_list = pkt_list  # packet list for sending
        self.tx_start = 0;  # pointer for first transmitted packet (tx_window)
        self.seq = 0  # pointer for next packet sequence (tx_window), 보낸 packet의 수
        self.next_available = 0  # time 에 관한 변수
        self.remained_bw = 0
        self.duplicate_ack = 0
        self.count = 0
        self.wait = False
        # variables for clients
        self.channel = Channel(bandwidth)

        # variables for receivers
        self.ack_sequence = -1  # init, 받은 packet의 수
        self.retx = 0

        ############################### IMPLEMENT ##############################################
        # implement your own  congestion control with parameters!
        # note 1: you can use any variable from Packet() class
        # note 2: you may add additional variable into PACKET() class
        # note 3: you can use any additional parameter for congestion control e.g. avgRTT, etc.
        # note 4: you can adjust the current init values 
        ########################################################################################
        self.avgRTT = 4 * PROP_TIME  # RTT for 2 * (uplink.prop + downlink.prop)
        self.cwnd = 4  # init value
        # self.estimatedRTT = 0

    ############## IMPLEMENT ###############################
    # implement the send function of sender!
    # your job is to send the packets in terms of cwnd
    # note 1: sending without congestion control is provided
    #########################################################
    def send(self, t):
        # transmission is busy
        if t < self.next_available:
            return []  # empty list

        # transmission done
        if self.seq == PKT_NUMS:
            return []  # empty list

        if self.wait:
            return []
        # packets to transmit ( packets transmitted done? )
        pkts = []

        # next packet pointer init
        next_seq = 0

        # without congestion control: send packets with max bandwidth
        if self.cc == False:
            tx_time, num_packets, remained_bw = transmit(t, PKT_SIZE, self.channel, self.remained_bw)
            self.remained_bw = remained_bw

            for i in range(0, num_packets):
                self.pkt_list[self.seq].start_time = t
                self.pkt_list[self.seq].bs_arrival = t + tx_time + PROP_TIME
                pkts.append(self.pkt_list[self.seq])
                self.seq += 1
                if self.seq == PKT_NUMS:
                    break

            # next available transmit
            self.next_available = t + tx_time  # ms
        ############### IMPLEMENT #####################################
        # with congestion control: send packets with cwnd
        # implement your send function with congestion control! (cwnd)
        ###############################################################
        if self.cc == True:
            # if inflight packet # >= cwnd,
            if self.seq - self.tx_start >= self.cwnd:
                return []

            tx_time, num_packets, remained_bw = transmit(t, PKT_SIZE, self.channel, self.remained_bw)
            self.remained_bw = remained_bw

            for i in range(0, num_packets):
                self.pkt_list[self.seq].start_time = t
                self.pkt_list[self.seq].bs_arrival = t + tx_time + PROP_TIME
                pkts.append(self.pkt_list[self.seq])
                self.seq += 1
                if self.seq == PKT_NUMS:
                    break

            self.next_available = t + tx_time

        ###############################################################

        # return packet lists
        return pkts

    #################### IMPLEMENT recv() #######################
    # naive TCP ack generation is followed  
    # implement your own ack generation
    # note 1: you can add additional variables from observed data
    # note 2: you can generate advanced ack
    # note 3: please refer chapter 9. Transport Layer
    #############################################################
    def recv(self, t, pkts):
        if len(pkts) == 0:
            return False  # no acks

        # generate ack packet
        # cumulative ack send only one acknowledgement
        ack = Packet(0, PKT_SIZE)
        arrival_time = pkts[0].recv_arrival
        start_time = pkts[0].start_time
        # implement here #
        for i in range(0, len(pkts)):
            if self.ack_sequence + 1 == pkts[i].seq:
                self.ack_sequence += 1
            else:
                self.retx += 1

        ack.start_time = start_time
        ack.ack_seq = self.ack_sequence + 1
        ack.ack_arrival = arrival_time + 2 * PROP_TIME

        # return ack
        return ack

    ################## IMPLEMENT congestion control #################
    # naive congestion control is followed
    # implement your own congestion control using the ack packet!
    ###################################################################
    def congestion_control(self, t, ack):


        loss = False

        if ack == False:
            return False

        print(ack.ack_seq)

        # return true if all the packets are transmitted to receiver
        if ack.ack_seq == PKT_NUMS:
            return True

        # without congestion control, simply measure avgRTT
        if self.cc == False:
            ack_seq = ack.ack_seq
            sum = 0
            for i in range(self.tx_start, ack_seq):
                sum += ack.ack_arrival - ack.start_time

            acked_packets = ack_seq - self.tx_start

            if acked_packets:
                self.avgRTT = int(sum / acked_packets)

            self.tx_start = ack_seq

            return False

        ########## IMPLEMENT ####################
        # naive congestion control are following
        # implement your own congestion control
        #########################################
        if self.cc == True:

            ack_seq = ack.ack_seq
            sum = 0
            for i in range(self.tx_start, ack_seq):
                sum += ack.ack_arrival - ack.start_time

            acked_packets = ack_seq - self.tx_start

            if acked_packets:
                self.avgRTT = int(sum / acked_packets)

            # parameter for cwnd
            my_decrease = 2
            retx_thresh = 3

            # get acknowledge packets
            next_tx_seq = self.seq
            ack_seq = ack.ack_seq

            if next_tx_seq != ack_seq:
                loss = True

            # real loss or fake loss(waiting at bs)
            if loss == True:
                # duplicate Ack but not real loss yet, may be real loss
                if self.duplicate_ack == ack_seq:
                    self.count += 1
                    if self.count != retx_thresh:
                        self.tx_start = ack_seq
                        self.wait = True
                        return False

                # no duplicate Ack, case of fake loss
                else:
                    self.duplicate_ack = ack_seq
                    self.tx_start = ack_seq
                    self.count = 1
                    self.wait = True
                    return False
                # real loss
                if self.count == retx_thresh:
                    self.cwnd = max(4, int(self.cwnd / my_decrease))
            # success
            else:
                self.cwnd += 2
            # success or real loss
            # remove ack packets from tx_window
            # restart from unacked packets

            self.tx_start = ack_seq
            self.seq = ack_seq
            self.duplicate_ack = ack_seq
            self.count = 1
            self.wait = False
        return False
