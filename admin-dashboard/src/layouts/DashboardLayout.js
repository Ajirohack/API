import React, { useState } from 'react';
import { useNavigate, useLocation, Link as RouterLink } from 'react-router-dom';
import {
    Box,
    Drawer,
    AppBar,
    Toolbar,
    List,
    Typography,
    Divider,
    IconButton,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Avatar,
    Menu,
    MenuItem,
    Container,
    useMediaQuery,
    useTheme as useMuiTheme
} from '@mui/material';
import {
    Menu as MenuIcon,
    Dashboard as DashboardIcon,
    Extension as PluginIcon,
    Schema as WorkflowIcon,
    SmartToy as AgentIcon,
    Storage as RagIcon,
    Settings as SettingsIcon,
    Brightness4 as DarkModeIcon,
    Brightness7 as LightModeIcon,
    AccountCircle,
    ChevronLeft as ChevronLeftIcon
} from '@mui/icons-material';

import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';

// Sidebar width
const drawerWidth = 240;

const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: <DashboardIcon /> },
    { name: 'Plugins', path: '/plugins', icon: <PluginIcon /> },
    { name: 'Workflows', path: '/workflows', icon: <WorkflowIcon /> },
    { name: 'Agents', path: '/agents', icon: <AgentIcon /> },
    { name: 'RAG System', path: '/rag', icon: <RagIcon /> },
    { name: 'Settings', path: '/settings', icon: <SettingsIcon /> },
];

const DashboardLayout = ({ children }) => {
    const { currentUser, logout } = useAuth();
    const { mode, toggleTheme } = useTheme();
    const muiTheme = useMuiTheme();
    const navigate = useNavigate();
    const location = useLocation();
    const [open, setOpen] = useState(true);
    const [anchorEl, setAnchorEl] = useState(null);
    const isSmallScreen = useMediaQuery(muiTheme.breakpoints.down('md'));

    // Close sidebar on small screens by default
    React.useEffect(() => {
        if (isSmallScreen) {
            setOpen(false);
        } else {
            setOpen(true);
        }
    }, [isSmallScreen]);

    const handleDrawerToggle = () => {
        setOpen(!open);
    };

    const handleMenuOpen = (event) => {
        setAnchorEl(event.currentTarget);
    };

    const handleMenuClose = () => {
        setAnchorEl(null);
    };

    const handleLogout = async () => {
        handleMenuClose();
        await logout();
        navigate('/login');
    };

    const handleProfile = () => {
        handleMenuClose();
        navigate('/settings');
    };

    return (
        <Box sx={{ display: 'flex' }}>
            <AppBar
                position="fixed"
                sx={{
                    zIndex: (theme) => theme.zIndex.drawer + 1,
                    transition: (theme) => theme.transitions.create(['width', 'margin'], {
                        easing: theme.transitions.easing.sharp,
                        duration: theme.transitions.duration.leavingScreen,
                    }),
                    ...(open && {
                        marginLeft: drawerWidth,
                        width: `calc(100% - ${drawerWidth}px)`,
                        transition: (theme) => theme.transitions.create(['width', 'margin'], {
                            easing: theme.transitions.easing.sharp,
                            duration: theme.transitions.duration.enteringScreen,
                        }),
                    }),
                }}
            >
                <Toolbar>
                    <IconButton
                        color="inherit"
                        aria-label="toggle drawer"
                        onClick={handleDrawerToggle}
                        edge="start"
                        sx={{ mr: 2 }}
                    >
                        {open ? <ChevronLeftIcon /> : <MenuIcon />}
                    </IconButton>
                    <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                        SpaceNew Admin
                    </Typography>

                    <IconButton onClick={toggleTheme} color="inherit">
                        {mode === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
                    </IconButton>

                    <IconButton
                        onClick={handleMenuOpen}
                        color="inherit"
                        edge="end"
                        aria-controls="user-menu"
                        aria-haspopup="true"
                    >
                        <Avatar
                            alt={currentUser?.full_name || 'User'}
                            src={currentUser?.avatar || ''}
                            sx={{ width: 32, height: 32 }}
                        >
                            {!currentUser?.avatar && (currentUser?.full_name?.[0] || <AccountCircle />)}
                        </Avatar>
                    </IconButton>

                    <Menu
                        id="user-menu"
                        anchorEl={anchorEl}
                        open={Boolean(anchorEl)}
                        onClose={handleMenuClose}
                        MenuListProps={{
                            'aria-labelledby': 'user-menu-button',
                        }}
                        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
                    >
                        <MenuItem onClick={handleProfile}>Profile</MenuItem>
                        <MenuItem onClick={handleLogout}>Logout</MenuItem>
                    </Menu>
                </Toolbar>
            </AppBar>
            <Drawer
                variant={isSmallScreen ? "temporary" : "persistent"}
                open={open}
                onClose={isSmallScreen ? handleDrawerToggle : undefined}
                sx={{
                    width: drawerWidth,
                    flexShrink: 0,
                    '& .MuiDrawer-paper': {
                        width: drawerWidth,
                        boxSizing: 'border-box',
                    },
                }}
            >
                <Toolbar />
                <Box sx={{ overflow: 'auto', mt: 2 }}>
                    <List>
                        {navItems.map((item) => {
                            const isActive = location.pathname === item.path;

                            return (
                                <ListItem key={item.name} disablePadding>
                                    <ListItemButton
                                        component={RouterLink}
                                        to={item.path}
                                        selected={isActive}
                                        sx={{
                                            borderRadius: '0 24px 24px 0',
                                            mr: 2,
                                            '&.Mui-selected': {
                                                backgroundColor: 'primary.light',
                                                color: 'primary.contrastText',
                                                '& .MuiListItemIcon-root': {
                                                    color: 'primary.contrastText',
                                                },
                                            },
                                            '&:hover': {
                                                backgroundColor: 'action.hover',
                                            }
                                        }}
                                    >
                                        <ListItemIcon sx={{ color: isActive ? 'primary.contrastText' : 'inherit' }}>
                                            {item.icon}
                                        </ListItemIcon>
                                        <ListItemText primary={item.name} />
                                    </ListItemButton>
                                </ListItem>
                            );
                        })}
                    </List>
                    <Divider sx={{ my: 2 }} />
                </Box>
            </Drawer>
            <Box
                component="main"
                sx={{
                    flexGrow: 1,
                    p: 3,
                    width: '100%',
                    minHeight: '100vh',
                    backgroundColor: (theme) => theme.palette.background.default,
                }}
            >
                <Toolbar />
                <Container maxWidth="xl">
                    {children}
                </Container>
            </Box>
        </Box>
    );
};

export default DashboardLayout;
