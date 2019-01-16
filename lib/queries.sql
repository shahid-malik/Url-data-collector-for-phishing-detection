ALTER TABLE package_features CHANGE url_title VARCHAR(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE package_features CHANGE domain_title domain_title VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;


insert into package_features (url_md5, url_base64, url_title, url_favicons, url_is_html, url_content_type, url_total_favicon, url_og_domains, url_total_og_domains, url_total_og_links, url_file_type, domain_md5, domain_base64, domain_title, domain_favicons, domain_is_html, domain_content_type, domain_total_favicon, domain_og_domains, domain_total_og_domains, domain_total_og_links, domain_file_type, landing_url_hash, landing_url_base64, title_match, uri_length, url_length, is_favicon_match,domain_entropy, url_entropy, timestamp, total_at_the_rate) VALUES ('70b29c430852cf6bb03c365cd0eb7e5a', 'aHR0cDovL21pbW9icmF6aWwuY29tLw==', '注册就送6元的|新注册就送彩金的彩票|注册就送88元体验金——[www.463.com]', '', 'True', 'text/html', '0', '693bb6289543b15968e0589ca251fe02,70b29c430852cf6bb03c365cd0eb7e5a,55f91633f393e525bfd1eec654ef8e15,a7fe4d20d6993e52cf72138c4da8f990,e967e7714d1dbce71d1675963648c73c,5aaa7b9a27b3ff8cac346a7c9d405422,d41d8cd98f00b204e9800998ecf8427e', '7', '158', 'text/html', '70b29c430852cf6bb03c365cd0eb7e5a', 'aHR0cDovL21pbW9icmF6aWwuY29tLw==', '注册就送6元的|新注册就送彩金的彩票|注册就送88元体验金——[www.463.com]', '', 'True', 'text/html', '0', '693bb6289543b15968e0589ca251fe02,70b29c430852cf6bb03c365cd0eb7e5a,55f91633f393e525bfd1eec654ef8e15,a7fe4d20d6993e52cf72138c4da8f990,e967e7714d1dbce71d1675963648c73c,5aaa7b9a27b3ff8cac346a7c9d405422,d41d8cd98f00b204e9800998ecf8427e', '7', '158', 'text/html', '70b29c430852cf6bb03c365cd0eb7e5a', 'aHR0cDovL21pbW9icmF6aWwuY29tLw==', 'True', '1', '22', '1', '3.75444184571', '3.75444184571', '2019-01-16 12:25:31', '0');


ALTER DATABASE b_classifier DEFAULT CHARACTER SET utf8
ALTER TABLE package_features DEFAULT CHARACTER SET utf8
alter table package_features modify column domain_favicons MEDIUMTEXT
set names utf8;