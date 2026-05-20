from dataclasses import dataclass


@dataclass
class LFRNetworkConfig:
    """
    Dataclass for LFR networks configurations.

    Attributes:
        description : (str)
            The description of the network.
        instance : (int)
            The instance number of the network.
        name : (str)
            The name of the network.
        overlapping_ground_truth : (bool)
            Whether the ground truth is overlapping.
    """

    description: str
    instance: int
    name: str
    overlapping_ground_truth: bool

    @staticmethod
    def from_dict(data):
        """
        Create a LFRNetworkConfig object from a dictionary.

        Parameters:
            data : (dict)
                The dictionary to create the Network from.

        Returns:
            network : (LFRNetworkConfig)
                The created LFRNetworkConfig.
        """

        return LFRNetworkConfig(
            description=data["description"],
            instance=data["instance"],
            name=data["name"],
            overlapping_ground_truth=data["overlapping_ground_truth"],
        )


@dataclass
class LFRNetworkFamilyConfig:
    """
    Dataclass for LFR network family configuration.

    Attributes:
        name : (str)
            The name of the network family.
        network_configs : (list[LFRNetworkConfig])
            The list of network configs in the family.

    Returns:
        network_family : (LFRNetworkFamilyConfig)
            The created LFRNetworkFamilyConfig.
    """

    name: str
    network_configs: list[LFRNetworkConfig]

    @staticmethod
    def from_dict(data):
        """
        Create a LFRNetworkFamilyConfig object from a dictionary.

        Parameters:
            data : dict
                The dictionary to create the NetworkFamily from.

        Returns:
            network_family : NetworkFamily
                The created NetworkFamily.
        """

        return LFRNetworkFamilyConfig(
            name=data["name"],
            network_configs=[LFRNetworkConfig.from_dict(x) for x in data["networks"]],
        )


@dataclass
class NetworkConfig:
    """
    Dataclass for real-world network configurations.

    Attributes:
        name : (str)
            The name of the network.
        gml_filename : (str)
            The name of the GML file associated with the network.
        ground_truth : (bool)
            Whether the network has ground-truth community labels.
        overlapping_ground_truth : (bool | None)
            Whether the ground-truth communities are overlapping, or None if the network does not have ground-truth community labels.
        ground_truth_attr : (str | None)
            The node attribute containing the ground-truth community label, or None if the network does not have ground-truth community labels.
    """

    name: str
    gml_filename: str
    ground_truth: bool
    overlapping_ground_truth: bool
    ground_truth_attr: str

    @staticmethod
    def from_dict(data):
        """
        Create a NetworkConfig object from a dictionary.

        Parameters:
            data : (dict)
                The dictionary containing the network configuration.

        Returns:
            network : (NetworkConfig)
                The created NetworkConfig.
        """

        return NetworkConfig(
            name=data["name"],
            gml_filename=data['gml_filename'],
            ground_truth=data['ground_truth'],
            overlapping_ground_truth=data.get('overlapping_ground_truth', None),
            ground_truth_attr=data.get('ground_truth_attr', None),
        )


@dataclass
class NetworkFamilyConfig:
    """
    Dataclass for network family configuration.

    Attributes:
        name : (str)
            The name of the network family.
        directory : (str)
            The directory of the network family.
        network_configs : (list[Network])
            The list of network configs in the family.

    Returns:
        network_family : (NetworkFamily)
            The created NetworkFamily.
    """

    name: str
    directory: str
    network_configs: list[NetworkConfig]

    @staticmethod
    def from_dict(data, with_ground_truth_dir, without_ground_truth_dir):
        """
        Create a NetworkConfig object from a dictionary.

        Parameters:
            data : (dict)
                The dictionary to create the NetworkFamily from.
            with_ground_truth_dir : (str)
                The directory of the networks with ground truth.
            without_ground_truth_dir : (str)
                The directory of the networks without ground truth.

        Returns:
            network_family : (NetworkFamily)
                The created NetworkFamily.
        """

        return NetworkFamilyConfig(
            name=data["name"],
            directory=with_ground_truth_dir if data["ground_truth_family"] else without_ground_truth_dir,
            network_configs=[NetworkConfig.from_dict(x) for x in data["networks"]],
        )
