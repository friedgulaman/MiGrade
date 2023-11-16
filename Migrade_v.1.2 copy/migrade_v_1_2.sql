-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 09, 2023 at 01:24 PM
-- Server version: 10.4.27-MariaDB
-- PHP Version: 8.1.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `migrade_v.1.2`
--

-- --------------------------------------------------------

--
-- Table structure for table `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add content type', 4, 'add_contenttype'),
(14, 'Can change content type', 4, 'change_contenttype'),
(15, 'Can delete content type', 4, 'delete_contenttype'),
(16, 'Can view content type', 4, 'view_contenttype'),
(17, 'Can add session', 5, 'add_session'),
(18, 'Can change session', 5, 'change_session'),
(19, 'Can delete session', 5, 'delete_session'),
(20, 'Can view session', 5, 'view_session'),
(21, 'Can add user', 6, 'add_customuser'),
(22, 'Can change user', 6, 'change_customuser'),
(23, 'Can delete user', 6, 'delete_customuser'),
(24, 'Can view user', 6, 'view_customuser'),
(25, 'Can add teacher', 7, 'add_teacher'),
(26, 'Can change teacher', 7, 'change_teacher'),
(27, 'Can delete teacher', 7, 'delete_teacher'),
(28, 'Can view teacher', 7, 'view_teacher'),
(29, 'Can add admin', 8, 'add_admin'),
(30, 'Can change admin', 8, 'change_admin'),
(31, 'Can delete admin', 8, 'delete_admin'),
(32, 'Can view admin', 8, 'view_admin'),
(33, 'Can add student', 9, 'add_student'),
(34, 'Can change student', 9, 'change_student'),
(35, 'Can delete student', 9, 'delete_student'),
(36, 'Can view student', 9, 'view_student'),
(37, 'Can add grade section', 10, 'add_gradesection'),
(38, 'Can change grade section', 10, 'change_gradesection'),
(39, 'Can delete grade section', 10, 'delete_gradesection'),
(40, 'Can view grade section', 10, 'view_gradesection'),
(41, 'Can add grade', 11, 'add_grade'),
(42, 'Can change grade', 11, 'change_grade'),
(43, 'Can delete grade', 11, 'delete_grade'),
(44, 'Can view grade', 11, 'view_grade'),
(45, 'Can add section', 12, 'add_section'),
(46, 'Can change section', 12, 'change_section'),
(47, 'Can delete section', 12, 'delete_section'),
(48, 'Can view section', 12, 'view_section');

-- --------------------------------------------------------

--
-- Table structure for table `cuyabsrms_admin`
--

CREATE TABLE `cuyabsrms_admin` (
  `id` bigint(20) NOT NULL,
  `email` varchar(254) NOT NULL,
  `password` varchar(225) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `username_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `cuyabsrms_admin`
--

INSERT INTO `cuyabsrms_admin` (`id`, `email`, `password`, `created_at`, `updated_at`, `username_id`) VALUES
(1, 'ces_admin@gmail.com', '', '2023-09-18 00:54:13.072619', '2023-10-09 03:02:31.453310', 1);

-- --------------------------------------------------------

--
-- Table structure for table `cuyabsrms_customuser`
--

CREATE TABLE `cuyabsrms_customuser` (
  `id` bigint(20) NOT NULL,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `user_type` smallint(5) UNSIGNED NOT NULL CHECK (`user_type` >= 0),
  `middle_ini` varchar(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `cuyabsrms_customuser`
--

INSERT INTO `cuyabsrms_customuser` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`, `user_type`, `middle_ini`) VALUES
(1, 'pbkdf2_sha256$600000$mIP1fGjYINJKumVUwk0v5C$HNdMby0Z5X1djDTM0QUnSddSpXmC40Z0zcdNoNqEQm8=', '2023-10-09 03:02:31.416517', 1, 'ces_admin', '', '', 'ces_admin@gmail.com', 1, 1, '2023-09-18 00:54:12.391383', 1, NULL),
(9, 'pbkdf2_sha256$600000$1bgdeKaXpvee9GEvHWXCJJ$tmXj09do2SqwFM9gfIvgOhEas+wCv6b2+j4VX7maNbc=', '2023-09-19 08:58:50.364478', 0, 'test5', 'test5', 'test5', 'test5@gmail.com', 0, 1, '2023-09-18 09:26:28.887726', 2, 'S'),
(10, 'pbkdf2_sha256$600000$4Ssble9ScFHLtqpdfPSmkO$CGxh6tzr+eC8CohSMbSDR/lORfTSEvVPOEwTV2/ZiG8=', NULL, 0, 'test6', 'test6', 'test6', 'test6@gmail.com', 0, 1, '2023-09-18 09:28:10.125502', 2, 'S'),
(11, 'pbkdf2_sha256$600000$8qa7K3R739zQGyK06NPyBo$74yaypPwtyoeTYI5/eigfbfoBYLPFqXRh8fjhPmuLYw=', NULL, 0, 'test_username', 'test_fn', 'test_ln', 'test_username@gmail.com', 0, 1, '2023-09-18 09:32:31.729283', 2, 'S'),
(12, 'pbkdf2_sha256$600000$4Pekl4J4GINfWBRmUbyuFp$lpjm5pDy4dLoZFn/zWHlF9MP4I+cJgC6Dz9azQj+85s=', NULL, 0, 'test7', 'test7', 'test7', 'test7@gmail.com', 0, 1, '2023-09-18 09:33:50.552289', 2, 'Q'),
(14, 'pbkdf2_sha256$600000$tOiS1NSUM4qjLiiHYI1qaI$9KHmfki5GMWre5k5qKi6g/qdFRPNrEEcLUABrOun9mU=', NULL, 0, 'test12', 'test12', 'test12', 'test12@gmail.com', 0, 1, '2023-09-18 09:45:43.781542', 2, 'A'),
(15, 'pbkdf2_sha256$600000$n34HupaOIwYSnEvyxNeIZw$9YPFlFEX8e8/fUCp8ZWgIsgCynU/TjvGwu00WsC0P4w=', NULL, 0, 'test14', '', '', 'test14@gmail.com', 0, 1, '2023-09-18 10:24:34.895890', 2, 'X'),
(16, 'pbkdf2_sha256$600000$ymBMAxotaeULjLdguO7NdH$jwc5SVvL3rlZ56A5PN7+48GbdQfIC6lx4h6Sqi+fDvc=', NULL, 0, 'andrea', 'Andrea', 'Rivarez', 'andrea@gmail.com', 0, 1, '2023-09-18 10:43:48.471043', 2, 'V'),
(17, 'pbkdf2_sha256$600000$NhN8J4Q976aGxMQr2RuLgr$0ZwcHn2qs0Jt3PQa4j309Po/sDN258H+gN+t3U3CSoY=', NULL, 0, 'test20', 'test20', 'test20', 'test20@gmail.com', 0, 1, '2023-09-18 10:57:05.761032', 2, 'C'),
(18, 'pbkdf2_sha256$600000$CJk2zVc9Fa2wvDWEhhCwyU$dcq99nXU7ulAObo61d8+7petLXRnQguxWlFWf7jp0hk=', NULL, 0, 'test1', 'test1', 'test1', 'test1@gmail.com', 0, 1, '2023-09-18 10:59:58.185797', 2, 'A'),
(19, 'pbkdf2_sha256$600000$tOXG8h0EU22ftieFR3xq49$FhAvozN81JYUCr0PgRvyu7R8GwnAe5c9UcN0eJHdl64=', NULL, 0, 'test2', 'test2', 'test2', 'test2@gmail.com', 0, 1, '2023-09-18 11:04:44.884179', 2, 'S'),
(20, 'pbkdf2_sha256$600000$lQvTjcaeLAllBbSXEOCFc6$RQjN89x4CjlCI1Xw/LJ8cmFmjDH78ynyDTJF3Wy01cE=', NULL, 0, 'test3', 'test3', 'test3', 'test3@gmail.com', 0, 1, '2023-09-18 11:06:21.251062', 2, 'C'),
(22, 'pbkdf2_sha256$600000$XfQQv79z6zyBRz2zgs68xO$UbvUYJac9xRV3vJEKaAjXBDC2OKM+7/l3Wi9jwrvBOg=', NULL, 0, 'test_1', 'test_1', 'test_1', 'test_1@gmail.com', 0, 1, '2023-09-18 11:14:46.701051', 2, 'Q'),
(23, 'pbkdf2_sha256$600000$8pqEJ6g2yNyq0BFoVz5I3P$/48ld43uzK6O6cJ44U3HSLV/NDFTneY4cntqhhl485s=', NULL, 0, 'test_2', 'test_2', 'test_2', 'test_2@gmail.com', 0, 1, '2023-09-18 11:21:27.172210', 2, 'C'),
(24, 'pbkdf2_sha256$600000$gPd2OWKX38GJYjMhWNFwXq$xxEZ64kaXZ6TtJfpulWA+D04Zo/YsgF36Zn17MBi6sQ=', NULL, 0, 'andrea_ganda', 'andrea_ganda', 'andrea_ganda', 'andrea_ganda@gmail.com', 0, 1, '2023-09-18 11:31:31.134841', 2, 'V'),
(25, 'pbkdf2_sha256$600000$LPVRXsi4gJuHOnvTnohfRD$XX5gi/JMDC0dy8TvZqqE3dKMJ9rQRGCJC+Ve4kHOXWM=', NULL, 0, 'test_test', 'test', 'test', 'test_test@gmail.com', 0, 1, '2023-09-18 11:38:39.721653', 2, 'T'),
(26, 'pbkdf2_sha256$600000$yoPYJ8GwFlFr3yUmnkGmH5$BQqZQv4qhJ905JSmz9ORoZzS/MGclI5AmgssUVFToP8=', NULL, 0, 'test_21', 'test_21', 'test_21', 'test_21@gmail.com', 0, 1, '2023-09-18 11:44:28.583621', 2, 'Q'),
(27, 'pbkdf2_sha256$600000$43TqQg0kkClhroeLj0EvOg$lpJvgyUk1yOigEHKKdZK+JJHcLmxlc55oBloG1bkFuQ=', NULL, 0, 'john', 'john', 'eric', 'john@gmail.com', 0, 1, '2023-09-18 12:06:23.948391', 2, 's'),
(28, 'pbkdf2_sha256$600000$IcMgvR3ZTEU9exGi4xm8w7$jWYgabZuWb+Pp+oziUf1uSOWHMy3BMv+PViAaxma/KY=', NULL, 0, 'rivarez1', 'rivarez1', 'rivarez1', 'rivarez1@gmail.com', 0, 1, '2023-09-18 12:07:39.915385', 2, 'A'),
(29, 'pbkdf2_sha256$600000$Imb2GkLdnK1whFBPP9ErCo$KycjtQIGnRLmshaczUMtlVOta39UG1GU4nBVCer+NvQ=', NULL, 0, '1', '1', '1', '1@gmail.com', 0, 1, '2023-09-18 12:11:22.495335', 2, 'A'),
(30, 'pbkdf2_sha256$600000$Yxm7ESyZGaoYULr3aenu4X$3xDe/Xbw7zFPz1y7qga6M8XOarYBYh18E0COkoo2Bx8=', NULL, 0, 'test_user', 'test', 'user', 'test_user@gmail.com', 0, 1, '2023-09-19 08:22:45.319754', 2, 'S'),
(31, 'pbkdf2_sha256$600000$g8zdFfZaZ14NfhlZvjIbC6$UxuJwVyj/RpAWyTwTcudQ9/S3MMXUalZy29MIpJb/I8=', NULL, 0, 'w', 'q', 'q', 'w@gmail.com', 0, 1, '2023-09-19 08:27:46.801478', 2, 'q'),
(33, 'pbkdf2_sha256$600000$cTLnazzr3lPmb5hiyw5NX2$OLJU+Aj8u67P1L0igyRmPBqShXLvCIIQE0kw0c5YbEU=', NULL, 0, 'qw', 'wqw', 'wqwq', 'wq@gmai.com', 0, 1, '2023-09-19 08:32:17.715100', 2, 'q'),
(35, 'pbkdf2_sha256$600000$6WHzG53uTVheOXBhKaL8NM$YC66nZ/LKeFJ/rCiACmffhR27K/bvVlCYd1C4O1RIpQ=', NULL, 0, 'wqwqwqwqwq', 'wqwqqe', 'wqeqe', 'asadf@gmail.com', 0, 1, '2023-09-19 08:33:41.865970', 2, 'w'),
(37, 'pbkdf2_sha256$600000$yN8aOEZQAvrtg2OYiKqXEn$osDo8WPnWRY1GOugAJOGNZ/TVqXa8RYCjYtzidKfu8w=', NULL, 0, 'sfsdasdasd', 'dasd', 'dasdasd', 'dasdasds@adsdsa', 0, 1, '2023-09-19 08:36:14.066775', 2, 'e'),
(39, 'pbkdf2_sha256$600000$60ijeG5etjKpSTuiIBsuKc$P9zAVx//oqmLJ0fbj39WjY4sxLXXPLg7x6gkB5pFAUc=', NULL, 0, 'saquido', 'sa', 'quido', 'saquido@gmail.om', 0, 1, '2023-09-19 08:43:05.946641', 2, 'R'),
(41, 'pbkdf2_sha256$600000$Sd1W3XA2FqYZPFk2qz8NPL$0/Tew2AkWuH7BfGPPL2tLnQRS+LLSC2gv/7e4jmXGuE=', NULL, 0, 'wrqrw1w121', 'wrqrw1w121', 'wrqrw1w121', 'wrqrw1w121@gmail.com', 0, 1, '2023-09-19 08:48:15.030175', 2, 'Q'),
(43, 'pbkdf2_sha256$600000$z2Da6lBoxPAfN0tpb2sbtL$mMqQLGGC5emC40FjyAAC5rqeXjWsqIXxy08CdpiI0gY=', '2023-09-19 08:57:32.808427', 0, 'sasasas', 'asa', 'sasasa', 'asasas@gmailcom', 0, 1, '2023-09-19 08:51:28.071860', 2, 'a'),
(45, 'pbkdf2_sha256$600000$w0KEN3eFU4oAA4ZTPLdjQ0$aEu9e3JqjGL8T7jJsPf+utye/yJua51cTNNM4cxJk1E=', '2023-10-09 03:33:15.197730', 0, 'ericrivarez', 'eric', 'rivarez', 'ericrivarez17@gmail.com', 0, 1, '2023-09-19 11:18:00.060354', 2, 's'),
(46, 'pbkdf2_sha256$600000$0zd7RGsa4r2KCJGZvEbuFW$HHzmx9i6WA7kwyjMWrT0PvZuu7hk0yLxGf76+ip88Vc=', '2023-09-29 00:37:59.917822', 0, 'ijen', 'ijen', 'ortega', 'ijen@gmail.com', 0, 1, '2023-09-23 13:50:40.731553', 2, 'R'),
(47, 'pbkdf2_sha256$600000$1hHFcmqNbqEfLo6ieDBnTH$0ia6g/mPVVCHaO4gjI9UABcyCjz3LKY4B0uxTONrUQo=', NULL, 0, 'teacher_sunflower', 'sun', 'flower', 'sunflower@gmail.com', 0, 1, '2023-10-04 07:03:49.648424', 2, 'T');

-- --------------------------------------------------------

--
-- Table structure for table `cuyabsrms_customuser_groups`
--

CREATE TABLE `cuyabsrms_customuser_groups` (
  `id` bigint(20) NOT NULL,
  `customuser_id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `cuyabsrms_customuser_user_permissions`
--

CREATE TABLE `cuyabsrms_customuser_user_permissions` (
  `id` bigint(20) NOT NULL,
  `customuser_id` bigint(20) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `cuyabsrms_teacher`
--

CREATE TABLE `cuyabsrms_teacher` (
  `id` bigint(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `cuyabsrms_teacher`
--

INSERT INTO `cuyabsrms_teacher` (`id`, `created_at`, `updated_at`, `user_id`) VALUES
(40, '2023-09-19 11:18:00.664161', '2023-10-09 03:33:15.213803', 45),
(41, '2023-09-23 13:50:41.624551', '2023-09-29 00:37:59.917822', 46),
(42, '2023-10-04 07:03:50.236305', '2023-10-04 07:03:50.243230', 47);

-- --------------------------------------------------------

--
-- Table structure for table `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'admin', 'logentry'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(4, 'contenttypes', 'contenttype'),
(8, 'CuyabSRMS', 'admin'),
(6, 'CuyabSRMS', 'customuser'),
(11, 'CuyabSRMS', 'grade'),
(10, 'CuyabSRMS', 'gradesection'),
(12, 'CuyabSRMS', 'section'),
(9, 'CuyabSRMS', 'student'),
(7, 'CuyabSRMS', 'teacher'),
(5, 'sessions', 'session');

-- --------------------------------------------------------

--
-- Table structure for table `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2023-09-18 00:52:55.313224'),
(2, 'contenttypes', '0002_remove_content_type_name', '2023-09-18 00:52:55.479018'),
(3, 'auth', '0001_initial', '2023-09-18 00:52:55.990148'),
(4, 'auth', '0002_alter_permission_name_max_length', '2023-09-18 00:52:56.098425'),
(5, 'auth', '0003_alter_user_email_max_length', '2023-09-18 00:52:56.115423'),
(6, 'auth', '0004_alter_user_username_opts', '2023-09-18 00:52:56.117932'),
(7, 'auth', '0005_alter_user_last_login_null', '2023-09-18 00:52:56.149923'),
(8, 'auth', '0006_require_contenttypes_0002', '2023-09-18 00:52:56.153912'),
(9, 'auth', '0007_alter_validators_add_error_messages', '2023-09-18 00:52:56.170442'),
(10, 'auth', '0008_alter_user_username_max_length', '2023-09-18 00:52:56.187842'),
(11, 'auth', '0009_alter_user_last_name_max_length', '2023-09-18 00:52:56.220617'),
(12, 'auth', '0010_alter_group_name_max_length', '2023-09-18 00:52:56.275201'),
(13, 'auth', '0011_update_proxy_permissions', '2023-09-18 00:52:56.303404'),
(14, 'auth', '0012_alter_user_first_name_max_length', '2023-09-18 00:52:56.320968'),
(15, 'CuyabSRMS', '0001_initial', '2023-09-18 00:52:57.193248'),
(16, 'admin', '0001_initial', '2023-09-18 00:52:57.443855'),
(17, 'admin', '0002_logentry_remove_auto_add', '2023-09-18 00:52:57.485425'),
(18, 'admin', '0003_logentry_add_action_flag_choices', '2023-09-18 00:52:57.521989'),
(19, 'sessions', '0001_initial', '2023-09-18 00:52:57.604140'),
(20, 'CuyabSRMS', '0002_remove_teacher_password_customuser_middle_ini_and_more', '2023-09-18 09:25:14.286939'),
(21, 'CuyabSRMS', '0003_rename_username_teacher_user_and_more', '2023-09-19 08:31:01.642099'),
(22, 'CuyabSRMS', '0004_remove_teacher_email_remove_teacher_first_name_and_more', '2023-09-19 11:09:12.540035'),
(23, 'CuyabSRMS', '0005_student', '2023-09-28 13:45:45.732821'),
(24, 'CuyabSRMS', '0006_student_json_data', '2023-09-28 15:09:59.280293'),
(25, 'CuyabSRMS', '0007_student_teacher', '2023-09-29 00:18:59.147273'),
(26, 'CuyabSRMS', '0008_student_grade_student_section_alter_student_teacher', '2023-09-29 00:32:58.110839'),
(27, 'CuyabSRMS', '0009_alter_student_grade_alter_student_section', '2023-09-29 00:37:20.265716'),
(28, 'CuyabSRMS', '0010_gradesection', '2023-10-04 07:29:00.611308'),
(29, 'CuyabSRMS', '0011_alter_gradesection_grade_alter_gradesection_section', '2023-10-04 07:44:43.674812'),
(30, 'CuyabSRMS', '0012_grade_section_delete_gradesection', '2023-10-05 03:58:31.535356'),
(31, 'CuyabSRMS', '0013_section_teacher', '2023-10-08 05:22:13.253928');

-- --------------------------------------------------------

--
-- Table structure for table `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('0ykrpjpnmlp6hvdbd7yi1ed73s9denpw', 'e30:1qiVwj:SvfaBsPUFoocXJiFNO_aFuxnaaMFq6SIe-FF-NWFRoU', '2023-10-03 08:19:01.205731'),
('1pg7tyv5q1tlv567txb6guol92mlma91', 'e30:1qiAGT:YOAzWx5nhkTKqx7SjePndgqcTH_sKddutt0GQvYwAe4', '2023-10-02 09:09:57.899273'),
('1umz7bshemzp7hcv7ytr68ddzrqgxogy', 'e30:1qiCKy:fJ1g6WG0EJlkvkZl-lYVsqAlkXrSEIcPWcjqUQb1ZTo', '2023-10-02 11:22:44.658662'),
('53vy3jhxu7n1uwwl3w8hhetze6130c9i', 'e30:1qiYd7:D1269R6QnU9tOXkzbyyDv6qz9JUpky5fmxyvHDqwnL0', '2023-10-03 11:10:57.582942'),
('55eizs60sahl8r0zt9hp7bj3tfmtxekb', 'e30:1qiVrt:GOblRlFCf0rYwHNH1lEBlaGLEFW6ALWmq-wh76dm0Qo', '2023-10-03 08:14:01.609335'),
('6bb0njxclqc34hou8hqh8rvuytnfe08d', 'e30:1qiVvB:zAyQ1PET-jv1vmN3k9AYDNJ_5UUTPTkJ2TUmDWMLxEo', '2023-10-03 08:17:25.923653'),
('fp0y5k6ue61sslzk1tilyje16w62vy1q', 'e30:1qi3gU:Cbu5AHIbeuBXJjLXwuLEoBo0wbBiU8g-0knyCFAWMng', '2023-10-02 02:08:22.419564'),
('kzeoqtm2rc6md6jkd3w2dfz35o3l8nyq', '.eJxVjMsOwiAQRf-FtSG8Cy7d-w1kBgapGkhKuzL-uzbpQrf3nHNfLMK21rgNWuKc2ZkZy06_I0J6UNtJvkO7dZ56W5cZ-a7wgw5-7Zmel8P9O6gw6rcuTnit0QYrFZpk0JGF5JAK0gReF4FaZJJGuCCzltrnRJOlZCGooiR7fwAS7Dhd:1qph19:B4dtcU8XzmwuVUUqB0wpfaZjxtpw-ZpSiv6ArbZ1pLQ', '2023-10-23 03:33:15.218872'),
('n0yjew6vel7oz78ycxu7yxob11kn04o7', 'e30:1qiVhQ:IOeJu6MNlJg_5GifOB02B6DkMjAoMFVz3jTehBwJ7VY', '2023-10-03 08:03:12.641993'),
('s3rxc6dmifp0kwfuyrysixiraeodctet', 'e30:1qiWVt:YN2Wfv42oBHWEZp8eajUQEoLJvSEbUfIXv0z9M3xfLU', '2023-10-03 08:55:21.567580'),
('vdh1wa28zywwqmq3v74mv1spddeolj1m', 'e30:1qiVns:XGdR0FxyomwvZolE0ZD75H82q5pJlng7qz6QFWoFx98', '2023-10-03 08:09:52.156213'),
('zfuenonhf1169khz7mu132pfntmnjraf', 'e30:1qiVT2:RPFWxGBzYfOb_KEDfuFB3xa3qwMi_sEx5pM-XlqmbMY', '2023-10-03 07:48:20.780516'),
('zu8vf1nc3br8uww7jd7ed0zwzpfsbnjr', 'e30:1qiVi9:NK0QMo7LJY2oKhdGt0CqEwrP-CaACEjtf44ISRsJSvE', '2023-10-03 08:03:57.093884');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Indexes for table `cuyabsrms_admin`
--
ALTER TABLE `cuyabsrms_admin`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username_id` (`username_id`),
  ADD UNIQUE KEY `CuyabSRMS_admin_email_feb74a05_uniq` (`email`);

--
-- Indexes for table `cuyabsrms_customuser`
--
ALTER TABLE `cuyabsrms_customuser`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `cuyabsrms_customuser_groups`
--
ALTER TABLE `cuyabsrms_customuser_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `CuyabSRMS_customuser_groups_customuser_id_group_id_e160cc74_uniq` (`customuser_id`,`group_id`),
  ADD KEY `CuyabSRMS_customuser_groups_group_id_ed5d9ee0_fk_auth_group_id` (`group_id`);

--
-- Indexes for table `cuyabsrms_customuser_user_permissions`
--
ALTER TABLE `cuyabsrms_customuser_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `CuyabSRMS_customuser_use_customuser_id_permission_35a78e65_uniq` (`customuser_id`,`permission_id`),
  ADD KEY `CuyabSRMS_customuser_permission_id_68818f38_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `cuyabsrms_teacher`
--
ALTER TABLE `cuyabsrms_teacher`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username_id` (`user_id`);

--
-- Indexes for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_CuyabSRMS_customuser_id` (`user_id`);

--
-- Indexes for table `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- Indexes for table `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=49;

--
-- AUTO_INCREMENT for table `cuyabsrms_admin`
--
ALTER TABLE `cuyabsrms_admin`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `cuyabsrms_customuser`
--
ALTER TABLE `cuyabsrms_customuser`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=48;

--
-- AUTO_INCREMENT for table `cuyabsrms_customuser_groups`
--
ALTER TABLE `cuyabsrms_customuser_groups`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `cuyabsrms_customuser_user_permissions`
--
ALTER TABLE `cuyabsrms_customuser_user_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `cuyabsrms_teacher`
--
ALTER TABLE `cuyabsrms_teacher`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=43;

--
-- AUTO_INCREMENT for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=32;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Constraints for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Constraints for table `cuyabsrms_admin`
--
ALTER TABLE `cuyabsrms_admin`
  ADD CONSTRAINT `CuyabSRMS_admin_username_id_c4d3537b_fk_CuyabSRMS_customuser_id` FOREIGN KEY (`username_id`) REFERENCES `cuyabsrms_customuser` (`id`);

--
-- Constraints for table `cuyabsrms_customuser_groups`
--
ALTER TABLE `cuyabsrms_customuser_groups`
  ADD CONSTRAINT `CuyabSRMS_customuser_customuser_id_2560a87a_fk_CuyabSRMS` FOREIGN KEY (`customuser_id`) REFERENCES `cuyabsrms_customuser` (`id`),
  ADD CONSTRAINT `CuyabSRMS_customuser_groups_group_id_ed5d9ee0_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Constraints for table `cuyabsrms_customuser_user_permissions`
--
ALTER TABLE `cuyabsrms_customuser_user_permissions`
  ADD CONSTRAINT `CuyabSRMS_customuser_customuser_id_3871b3f7_fk_CuyabSRMS` FOREIGN KEY (`customuser_id`) REFERENCES `cuyabsrms_customuser` (`id`),
  ADD CONSTRAINT `CuyabSRMS_customuser_permission_id_68818f38_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`);

--
-- Constraints for table `cuyabsrms_teacher`
--
ALTER TABLE `cuyabsrms_teacher`
  ADD CONSTRAINT `CuyabSRMS_teacher_user_id_d8e37739_fk_CuyabSRMS_customuser_id` FOREIGN KEY (`user_id`) REFERENCES `cuyabsrms_customuser` (`id`);

--
-- Constraints for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_CuyabSRMS_customuser_id` FOREIGN KEY (`user_id`) REFERENCES `cuyabsrms_customuser` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
