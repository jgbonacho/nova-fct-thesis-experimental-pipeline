from dataclasses import dataclass


@dataclass
class Network:
    """
    Dataclass for networks.

    Attributes:
        name : str
            The name of the network.
        overlapping_ground_truth : bool
            Whether the ground truth is overlapping.
    """

    name: str
    overlapping_ground_truth: bool

    @staticmethod
    def from_dict(data):
        """
        Create a Network from a dictionary.

        Parameters:
            data : dict
                The dictionary to create the Network from.

        Returns:
            network : Network
                The created Network.
        """

        return Network(
            name=data["name"],
            overlapping_ground_truth=data["overlapping_ground_truth"],
        )


@dataclass
class NetworkFamily:
    """
    Dataclass for network family.

    Attributes:
        name : str
            The name of the network family.
        networks : list[Network]
            The list of networks in the family.

    Returns:
        network_family : NetworkFamily
            The created NetworkFamily.
    """

    name: str
    networks: list[Network]

    @staticmethod
    def from_dict(data):
        """
        Create a NetworkFamily from a dictionary.

        Parameters:
            data : dict
                The dictionary to create the NetworkFamily from.

        Returns:
            network_family : NetworkFamily
                The created NetworkFamily.
        """

        return NetworkFamily(
            name=data["name"],
            networks=[Network.from_dict(x) for x in data["networks"]],
        )
