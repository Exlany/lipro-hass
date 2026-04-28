"""Property-path light entity behavior assertions."""

from __future__ import annotations

from unittest.mock import MagicMock


class TestLiproLightEntityProperties:
    """Tests for LiproLight entity property methods."""

    def test_brightness_ha_scale(self, mock_coordinator, make_device):
        """Test brightness returns HA scale (0-255) from device (0-100)."""
        device = make_device("light", properties={"brightness": "50"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        # 50% -> round(50 * 255 / 100) = 128
        assert light.brightness == 128

    def test_brightness_full(self, mock_coordinator, make_device):
        """Test brightness at 100% returns 255."""
        device = make_device("light", properties={"brightness": "100"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        assert light.brightness == 255

    def test_brightness_clamped_above_100(self, mock_coordinator, make_device):
        """Brightness above 100% should be clamped to 255 in HA scale."""
        device = make_device("light", properties={"brightness": "150"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        assert light.brightness == 255

    def test_brightness_clamped_below_0(self, mock_coordinator, make_device):
        """Brightness below 0% should be clamped to 0 in HA scale."""
        device = make_device("light", properties={"brightness": "-10"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        assert light.brightness == 0

    def test_is_on_property(self, mock_coordinator, make_device):
        """Test is_on reflects device power state."""
        device = make_device("light", properties={"powerState": "1"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        assert light.is_on is True

    def test_extra_state_attributes_off_state_no_tip_color_temp(
        self, mock_coordinator, make_device
    ):
        """No extra attributes are exposed for plain lights in off-state."""
        device = make_device("light", properties={"powerState": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        assert light.extra_state_attributes is None

    def test_extra_state_attributes_off_state_no_tip_brightness_only(
        self, mock_coordinator, make_device
    ):
        """Brightness-only lights should also rely on the base None behavior."""
        device = make_device(
            "light",
            properties={"powerState": "0"},
            min_color_temp_kelvin=0,
            max_color_temp_kelvin=0,
        )
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        assert light.extra_state_attributes is None

    def test_extra_state_attributes_on_state_no_tip(
        self, mock_coordinator, make_device
    ):
        """On-state plain lights still expose no extra attributes."""
        device = make_device("light", properties={"powerState": "1"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        assert light.extra_state_attributes is None

    def test_supported_color_modes_with_color_temp(self, mock_coordinator, make_device):
        """Test supported_color_modes includes COLOR_TEMP when device supports it."""
        from homeassistant.components.light.const import ColorMode

        device = make_device("light", properties={"temperature": "50"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        assert ColorMode.COLOR_TEMP in light.supported_color_modes

    def test_color_mode_property(self, mock_coordinator, make_device):
        """Test color_mode returns correct mode based on device capability."""
        from homeassistant.components.light.const import ColorMode

        device = make_device("light", properties={"temperature": "50"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        if device.supports_color_temp:
            assert light.color_mode == ColorMode.COLOR_TEMP
        else:
            assert light.color_mode == ColorMode.BRIGHTNESS

    def test_color_temp_kelvin_property(self, mock_coordinator, make_device):
        """Test color_temp_kelvin returns device color temp."""
        device = make_device("light", properties={"temperature": "50"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        if device.supports_color_temp:
            assert light.color_temp_kelvin == device.color_temp

    def test_fan_light_unique_id_has_suffix(self, mock_coordinator, make_device):
        """Test fan light entity has '_light' suffix in unique_id."""
        device = make_device("fanLight")
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        unique_id = light.unique_id
        assert unique_id is not None
        assert unique_id.endswith("_light")

    def test_regular_light_no_suffix(self, mock_coordinator, make_device):
        """Test regular light entity has no suffix in unique_id."""
        device = make_device("light")
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        assert light.unique_id == device.unique_id
