### MultiHop-Simulator


Source code of the MultiHop-Simulator to validate and reproduce some of the results in Tripathi et al. "Information Freshness in Multihop Wireless Networks" [[1]](#1).

## Age-Debt Policy and Simulator Validation Results

In this section, we discuss the multi-hop network version of the Age-Debt policy and present simulation results using our simulator to reproduce the results in [[1]](#1) to validate the simulator.

### Age-Debt Policy for Multihop Networks

In the Age-Debt policies for multihop networks, Tripathi et al. [[1]](#1) define virtual queues for each intermediate node. This virtual queue tracks both the current Age-Debt at the destination node and the potential reduction in debt due to the reception of a fresh packet at the destination. The age for a source node $s$ at an intermediate node $i$ is defined as $A_{i}^{s}(t)$ which evolves as follows:


```math
A_{i}^{s}(t+1) = \left\{
    \begin{array}{ll}
        \min(A_{i}^{s}(t), t - t_g) + 1, & \text{if the update packet generated at time } t_g \text{ is delivered successfully.} \\
        A_{i}^{s}(t) + 1, & \text{if no update packet is delivered}
    \end{array}
\right.
```

An Age-Debt queue $Q^{s \rightarrow i} (t)$ at an intermediate node $i$ for a source $s$ is defined as:

```math
Q^{s \rightarrow i} (t+1) = \left[ Q^{s \rightarrow i} (t) + \min \{A_{i}^{s}(t), A_{0}^{s}(t) \} + h_{i}^L -\alpha_s \right]^{+}
```

where $L$ is the set of adjacent links where node $i$ forwards the packets of source $s$, and $h_{i}^L$ represents the minimum hop count required from node $i$ to reach destination $0$. Typically, $h_{i}^L$ measures the delay of the packet from $s$ to reach the destination node $0$.

If node $i$ does not forward any packet to its adjacent nodes, the evolution is defined as:

``` math 
Q^{s \rightarrow i} (t+1) = \left[Q^{s \rightarrow i} (t)  + A_0^s(t+1) - \alpha_s \right] ^{+}
```

Considering the drift for every intermediate node $Q_0^{s \rightarrow i} (t)$, the equation is modified as:

``` math 
L(t) \triangleq \sum_{s=1}^{M} \left(  (Q_0^{s}(t))^2 + \sum_{{i\neq 0},i \neq s} (Q_0^{s \rightarrow i} (t))^2 \right)
```

The Age-Debt policy chooses an activation set to minimize the Lyapunov drift:

``` math 
U(t) = \underset{U \in \mathbb{U}}{\arg\min} \left( L_{U}(t + 1) - L(t) \right)
  
```

### Stationary Randomized Policies
In [[1]](#1), the authors used stationary randomized policies over a multihop network. Let $\mathcal{E}^{s}_{i,j}(t)$ be the event that chooses transmission source $s$ on a link $(i,j)$ at timeslot $t$. The stationary randomized policy is defined as $\pi$. Such that the events $`\mathcal{E}^{s}_{i,j}(t)`$ and $`\mathcal{E}^{s}_{i,j} (t')`$ happen independently and are stationary for any $t \neq t'$, for all sources $s$ and links $(i,j)$. The probability of these events is given by:

``` math 
\mathbb{P} [\mathcal{E}^{s}_{i,j} (t)] = \mathbb{P} [\mathcal{E}^{s}_{i,j}(t')] = f^{s}_{(i,j)}
```

where $`f^{s}_{(i,j)}`$ is the link activation frequency of link $(i,j)$ for source $s$. The link activation frequency $f^{s}_{(i,j)}$ for all links $(i,j)$ and sources $s$ is given by:

``` math 
f^{s}_{(i,j)} = \sum_{u \in {U}_{t}} x_u
```

Thus, let $\pi$ be the stationary randomized policy with link activation frequencies $\{f^{s}_{(i,j)}\}$. The average age for source $s$ is given by:

``` math 
A_{\text{ave}}^{s} = \lim_{{T \rightarrow \infty}} \mathbb{E}\left[\frac{1}{T} \sum_{{t = 1}}^{T} {A_0^s(t)}\right] = \sum _{(i,j) \in \mathcal{E}} \frac{1}{f^{s}_{(i,j)}}
```

### Validation Results

In [[1]](#1), two interference scenarios were considered for the evaluation. The first scenario corresponds to a one-hop or primary interference model, where only odd-numbered nodes or even-numbered nodes can forward data packets in any given time slot. This is similar to our $K$-hop interference constraint with $K=1$. In the second scenario, all nodes in the network interfere with each other, allowing only one node to forward the packet in any given time slot, similar to $K$-hop interference constraint with $K=\text{Complete Interference}$.

#### Simulation Results

![Reproduced Age-Difference and Age-Debt Policy Results](https://github.com/nibin-raj/MultiHop-Simulator/tree/main/figures/agediff_agedebt_khop1_linenetwork.png)
*Reproduced Age-Difference and Age-Debt policy results for a single-source scenario with $`K`$-hop interference constraint where $`K=1`$, showing similar results as given in [Figure 8 from [[1]](#1)].*

![Reproduced Stationary Randomized Policy](https://github.com/nibin-raj/MultiHop-Simulator/tree/main/figures/Randomized_policylinenetwork_comparison.png)
*Reproduced stationary randomized policy and its numerical plot according to [Eq. (7) from [[1]](#1)].*



## References
<a id="1">[1]</a> 
V. Tripathi et.al., "Information Freshness in Multihop Wireless Networks,", in IEEE/ACM Transactions on Networking, vol. 31, no. 2, pp. 784-799, April 2023, 
 doi: 10.1109/TNET.2022.3201751.

## Acknowledgment

This work is supported by the IIT-Palakkad IPTIF grant IPTIF/HRD/DF/022.
