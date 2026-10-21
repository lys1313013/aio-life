-- 设计草案：对现有sys_activity_log执行一次增量，未纳入后端升级计划。
-- 执行前核对现有字段、索引与实际迁移记录；中断后先查结构，不能直接重放。
-- 新字段允许NULL，兼容历史数据、ACCESS日志和旧版本实例。
ALTER TABLE `sys_activity_log`
    ADD COLUMN `request_method` varchar(16) DEFAULT NULL COMMENT 'HTTP方法，历史未采集为NULL' AFTER `request_path`,
    ADD COLUMN `request_params` json DEFAULT NULL COMMENT '白名单脱敏参数，应用限制32KiB' AFTER `request_method`,
    ADD COLUMN `request_time` datetime(3) DEFAULT NULL COMMENT '服务端请求接收时间，Asia/Shanghai' AFTER `request_params`,
    ADD COLUMN `duration_ms` int DEFAULT NULL COMMENT '处理耗时毫秒，非负，0有效，NULL未采集' AFTER `request_time`,
    ADD COLUMN `server_ip` varchar(64) DEFAULT NULL COMMENT '处理请求的后端实例IPv4或IPv6' AFTER `duration_ms`,
    ADD INDEX `idx_activity_type_req_time` (`log_type`, `is_deleted`, `request_time`, `id`);
